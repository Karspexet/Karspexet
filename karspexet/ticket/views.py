# coding: utf-8
import io
import json
import logging
import pdfkit
import pyqrcode


from dateutil import parser
from dateutil.relativedelta import relativedelta

from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.shortcuts import redirect
from django.template.response import HttpResponse, TemplateResponse
from django.utils import timezone

from karspexet.show.models import Show
from karspexet.ticket.models import Reservation, PricingModel, InvalidVoucherException, AlreadyDiscountedException, Voucher
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


def select_seats(request, show_slug):
    show = Show.objects.get(slug=show_slug)
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
            return redirect("booking_overview", show_slug=show.slug)

    taken_seats = set(map(int,set().union(*[r.tickets.keys() for r in taken_seats_qs.all()])))

    pricings, seats = _build_pricings_and_seats(show.venue)

    return TemplateResponse(request, "ticket/select_seats.html", {
        'taken_seats': list(taken_seats),
        'show': show,
        'venue': show.venue,
        'pricings': pricings,
        'seats': json.dumps(seats)
    })


def booking_overview(request, show_slug):
    show = Show.objects.get(slug=show_slug)
    reservation = _get_or_create_reservation_object(request, show)

    if _session_expired(request):
        messages.warning(request, "Du har väntat för länge, så din bokning har tröttnat och gått och lagt sig. Du får börja om från början!")
        return redirect("select_seats", show_slug=show_slug)

    _set_session_timeout(request)

    if not reservation.tickets:
        messages.warning(request, "Du måste välja minst en plats")
        return redirect("select_seats", show_slug=show_slug)

    reserved_seats = {seat.id:seat for seat in reservation.seats()}

    seats = ["%s: %s (%s, %dkr)" % (reserved_seats[int(id)].group.name, reserved_seats[int(id)].name, ticket_type, reserved_seats[int(id)].price_for_type(ticket_type)) for (id, ticket_type) in reservation.tickets.items()]

    return TemplateResponse(request, 'ticket/payment.html', {
        'seats': seats,
        'payment_partial': _payment_partial(reservation),
        'reservation': reservation,
        'stripe_key': stripe_keys['publishable_key'],
    })


@transaction.atomic
def apply_voucher(request, reservation_id):
    reservation = Reservation.objects.get(pk=reservation_id)
    show = reservation.show

    if _session_expired(request):
        messages.warning(request, "Du har väntat för länge, så din bokning har tröttnat och gått och lagt sig. Du får börja om från början!")
        return redirect("select_seats", show_slug=show.slug)

    if request.method == "POST":
        try:
            code = request.POST["voucher_code"]
            reservation.apply_voucher(code)
            reservation.save()
        except KeyError:
            messages.error(request, "För att kunna få rabatt måste du fylla i ett presentkort")
        except InvalidVoucherException:
            messages.error(request, "Presentkortet har redan använts")
        except AlreadyDiscountedException:
            messages.error(request, "Du har redan använt ett presentkort")
        except Voucher.DoesNotExist:
            messages.error(request, "Ogiltigt presentkort")

    return redirect("booking_overview", show_slug=show.slug)


def process_payment(request, reservation_id):
    reservation = Reservation.objects.get(pk=reservation_id)

    if _session_expired(request):
        messages.warning(request, "Du har väntat för länge, så din bokning har tröttnat och gått och lagt sig. Du får börja om från början!")
        return redirect("select_seats", show_slug=reservation.show.slug)

    if request.method == 'POST':
        try:
            reservation = PaymentProcess.run(reservation, request.POST, request)
            request.session['reservation_timeout'] = None
            request.session[f'show_{reservation.show_id}'] = None
            messages.success(request, "Betalningen lyckades!")

            return redirect("reservation_detail", reservation_code=reservation.reservation_code)

        except PaymentError as error:
            logger.exception(error, exc_info=True, extra={
                'request': request
            })
            return TemplateResponse(request, "ticket/payment.html", {
                'reservation': reservation,
                'seats': reservation.seats(),
                'payment_partial': _payment_partial(reservation),
                'stripe_key': stripe_keys['publishable_key'],
                'payment_failed': True,
            })


def reservation_detail(request, reservation_code):
    reservation = Reservation.objects.get(reservation_code=reservation_code)

    return TemplateResponse(request, "reservation_detail.html", {
        'reservation': reservation,
        'show': reservation.show,
        'venue': reservation.show.venue,
        'production': reservation.show.production,
        'tickets': reservation.ticket_set(),
    })


def ticket_detail(request, reservation_id, ticket_code):
    reservation = Reservation.objects.get(pk=reservation_id)
    ticket = reservation.ticket_set().get(ticket_code=ticket_code)

    return TemplateResponse(request, "ticket_detail.html", {
        'reservation': reservation,
        'show': reservation.show,
        'venue': reservation.show.venue,
        'production': reservation.show.production,
        'ticket': ticket,
        'seat': ticket.seat,
        'qr_code': _qr_code(request)
    })


def ticket_pdf(request, reservation_id, ticket_code):
    reservation = Reservation.objects.get(pk=reservation_id)
    ticket = reservation.ticket_set().get(ticket_code=ticket_code)

    template = TemplateResponse(request, "ticket_detail.html", {
            'reservation': reservation,
            'show': reservation.show,
            'venue': reservation.show.venue,
            'production': reservation.show.production,
            'ticket': ticket,
            'seat': ticket.seat,
            'qr_code': _qr_code(request)
        },
        content_type="utf-8"
    ).render()

    pdfkit_options = {
        'page-size': 'A5',
        'dpi': '300',
    }

    content = template.rendered_content

    if settings.WKHTMLTOPDF_PATH:
        pdfkit_config = pdfkit.configuration(wkhtmltopdf=settings.WKHTMLTOPDF_PATH)
        pdf = pdfkit.from_string(content, False, pdfkit_options, configuration=pdfkit_config)
    else:
        pdf = pdfkit.from_string(content, False, pdfkit_options)

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'inline;filename=karspexet-bokning-{}-{}.pdf'.format(reservation_id, ticket_code)

    return response


def cancel_reservation(request, show_id):
    session_key = f'show_{show_id}'
    if request.method == "POST":
        request.session[session_key] = None
        request.session['reservation_timeout'] = None

    reservation_id = request.session.get(session_key)
    if reservation_id:
        Reservation.objects.filter(pk=reservation_id).delete()
    return redirect("ticket_home")


def _session_expired(request):
    timeout = request.session.get('reservation_timeout', None)
    if timeout:
        timeout = parser.parse(timeout)
        return timeout < timezone.now()


def _set_session_timeout(request):
    request.session['reservation_timeout'] = (timezone.now() + relativedelta(minutes=SESSION_TIMEOUT_MINUTES)).isoformat()


def _get_or_create_reservation_object(request, show):
    timeout = timezone.now() + relativedelta(minutes=SESSION_TIMEOUT_MINUTES)
    session_key = f'show_{show.id}'
    reservation_id = request.session.get(session_key)

    if reservation_id:
        try:
            reservation = Reservation.objects.get(pk=reservation_id)
            reservation.session_timeout = timeout
            reservation.save()
            return reservation
        except ObjectDoesNotExist:
            pass

    reservation = Reservation.objects.create(show=show, tickets={}, session_timeout=timeout)
    request.session[session_key] = reservation.id

    return reservation


def _all_seats_available(qs, seat_ids):
    return not qs.filter(tickets__has_any_keys=seat_ids).exists()


def _seat_specifications(request):
    return {
        seat.replace("seat_", ""):ticket_type
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


def _payment_partial(reservation):
    if reservation.total == 0:
        return "_discount_payment.html"
    if settings.PAYMENT_PROCESS == "stripe":
        return "_stripe_payment.html"
    else:
        return "_fake_payment.html"


def _qr_code(request):
    url = pyqrcode.create(request.build_absolute_uri())
    buffer = io.BytesIO()
    url.svg(buffer, scale=4)
    return buffer.getvalue()
