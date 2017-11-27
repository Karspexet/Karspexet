# coding: utf-8
import json
import logging
import pdfkit

from dateutil import parser
from dateutil.relativedelta import relativedelta

from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect, render
from django.template.response import HttpResponse, TemplateResponse
from django.utils import timezone

from karspexet.show.models import Show
from karspexet.ticket.models import Reservation, PricingModel
from karspexet.ticket.payment import PaymentError, PaymentProcess
from karspexet.venue.models import Seat

if settings.PAYMENT_PROCESS == "stripe":
    stripe_keys = settings.ENV["stripe"]
else:
    stripe_keys = {"publishable_key": "fake", "secret_key": "fake"}


SESSION_TIMEOUT_MINUTES = 30

logger = logging.getLogger(__name__)


def home(request):
    upcoming_shows = Show.upcoming().filter(visible=True).all()

    return TemplateResponse(request, "ticket/ticket.html", {
        'upcoming_shows': upcoming_shows
    })


def select_seats(request, show_id):
    show = Show.objects.get(id=show_id)
    reservation = _get_or_create_reservation_object(request, show)
    taken_seats_qs = Reservation.active.exclude(pk=reservation.pk).filter(show=show)
    _set_session_timeout(request)

    if request.POST:
        seat_params = _seat_specifications(request)
        if not _all_seats_available(taken_seats_qs, seat_params.keys()):
            messages.error(request, "Vissa av platserna du valde har redan blivit bokade av någon annan")
        elif _some_seat_is_missing_ticket_type(seat_params):
            messages.error(request, "Du måste välja biljettyp för alla platser")
        else:
            reservation.tickets = seat_params
            reservation.save()
            return redirect("booking_overview")

    taken_seats = set(map(int,set().union(*[r.tickets.keys() for r in taken_seats_qs.all()])))

    pricings, seats = _build_pricings_and_seats(show.venue)

    return TemplateResponse(request, "ticket/select_seats.html", {
        'taken_seats': list(taken_seats),
        'show': show,
        'venue': show.venue,
        'pricings': pricings,
        'seats': json.dumps(seats)
    })


def booking_overview(request):
    reservation = _get_or_create_reservation_object(request)

    if _session_expired(request):
        messages.warning(request, "Du har väntat för länge, så din bokning har tröttnat och gått och lagt sig. Du får börja om från början!")
        return redirect("select_seats", show_id=reservation.show_id)

    _set_session_timeout(request)

    if not reservation.tickets:
        messages.warning(request, "Du måste välja minst en plats")
        return redirect("select_seats", show_id=reservation.show_id)

    reserved_seats = {seat.id:seat for seat in reservation.seats()}

    seats = ["%s (%s, %dkr)" % (reserved_seats[int(id)].name, ticket_type, reserved_seats[int(id)].price_for_type(ticket_type)) for (id, ticket_type) in reservation.tickets.items()]

    return TemplateResponse(request, 'ticket/payment.html', {
        'seats': seats,
        'payment_partial': _payment_partial(),
        'reservation': reservation,
        'stripe_key': stripe_keys['publishable_key'],
    })


def process_payment(request, reservation_id):
    reservation = Reservation.objects.get(pk=reservation_id)

    if _session_expired(request):
        messages.warning(request, "Du har väntat för länge, så din bokning har tröttnat och gått och lagt sig. Du får börja om från början!")
        return redirect("select_seats", show_id=reservation.show_id)

    if request.method == 'POST':
        try:
            reservation = PaymentProcess.run(reservation, request.POST, request)
            request.session['reservation_timeout'] = None
            request.session['reservation_id'] = None
            messages.success(request, "Betalningen lyckades!")

            return redirect("reservation_detail", reservation.reservation_code)

        except PaymentError as error:
            logger.exception(error)
            return TemplateResponse(request, "ticket/payment.html", {
                'reservation': reservation,
                'seats': reservation.seats(),
                'payment_partial': _payment_partial(),
                'stripe_key': stripe_keys['publishable_key'],
                'payment_failed': True,
            })


def reservation_detail(request, reservation_code):
    reservation = Reservation.objects.get(reservation_code=reservation_code)

    return TemplateResponse(request, "reservation_detail.html", {
        'reservation': reservation,
        'tickets': reservation.ticket_set(),
    })


def ticket_detail(request, reservation_code, ticket_id, render_pdf=""):
    reservation = Reservation.objects.get(reservation_code=reservation_code)
    ticket = reservation.ticket_set().get(pk=ticket_id)

    return TemplateResponse(request, "ticket_detail.html", {
        'reservation': reservation,
        'ticket': ticket,
    })


def ticket_pdf(request, reservation_code, ticket_id):
    reservation = Reservation.objects.get(reservation_code=reservation_code)
    ticket = reservation.ticket_set().get(pk=ticket_id)

    template = TemplateResponse(request, "ticket_detail.html", {
            'reservation': reservation,
            'ticket': ticket,
        },
        content_type="utf-8"
    ).render()

    pdfkit_options = {
        'page-size': 'A5',
        'dpi': '300',
    }

    # TODO: HTTP headers för unicode, linebreaks, etc
    content = template.rendered_content
    print(type(content))
    pdf = pdfkit.from_string(content, False, pdfkit_options)
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'inline;filename=karspexet-bokning-{}-{}.pdf'.format(reservation_code, ticket.id)

    return response

def _session_expired(request):
    timeout = request.session.get('reservation_timeout', None)
    if timeout:
        timeout = parser.parse(timeout)
        return timeout < timezone.now()


def _set_session_timeout(request):
    request.session['reservation_timeout'] = (timezone.now() + relativedelta(minutes=SESSION_TIMEOUT_MINUTES)).isoformat()


def _get_or_create_reservation_object(request, show=None):
    timeout = timezone.now() + relativedelta(minutes=SESSION_TIMEOUT_MINUTES)

    if request.session.get('reservation_id'):
        try:
            reservation = Reservation.objects.get(pk=request.session['reservation_id'])
            reservation.session_timeout = timeout
            reservation.save()
            return reservation
        except ObjectDoesNotExist:
            pass

    reservation = Reservation.objects.create(show=show, total=0, tickets={}, session_timeout=timeout)
    request.session['reservation_id'] = reservation.id

    return reservation


def _all_seats_available(qs, seat_ids):
    return not qs.filter(tickets__has_any_keys=seat_ids).exists()


def _seat_specifications(request):
    return {
        int(seat.replace("seat_", "")):ticket_type
            for seat,ticket_type in request.POST.items()
            if seat.startswith("seat_")
    }


def _some_seat_is_missing_ticket_type(seat_params):
    return any(not ticket_type for ( seat,ticket_type ) in seat_params.items())


def _build_pricings_and_seats(venue):
    qs = PricingModel.objects.select_related('seating_group').filter(seating_group__venue_id=venue)
    pricings = {
        pricing.seating_group_id : pricing.prices
        for pricing in qs.all()
    }

    seats = {
        "seat-%d" % s.id: {"id": s.id, "name": s.name, "group": s.group_id}
        for s in Seat.objects.filter(group_id__in=pricings.keys())
    }

    return (pricings, seats)


def _payment_partial():
    if settings.PAYMENT_PROCESS == "stripe":
        return "_stripe_payment.html"
    else:
        return "_fake_payment.html"
