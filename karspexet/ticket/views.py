# coding: utf-8
import io
import json
import logging

import pdfkit
import pyqrcode
import stripe
from dateutil import parser
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect
from django.template.response import HttpResponse, TemplateResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from karspexet.show.models import Show
from karspexet.ticket import payment
from karspexet.ticket.forms import CustomerEmailForm
from karspexet.ticket.models import (AlreadyDiscountedException, InvalidVoucherException, PricingModel, Reservation,
                                     Voucher)
from karspexet.ticket.tasks import send_ticket_email_to_customer
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


@csrf_exempt
def stripe_webhooks(request):
    # https://stripe.com/docs/payments/handling-payment-events#build-your-own-webhook
    # https://stripe.com/docs/webhooks/build

    event = _parse_stripe_payload(request.body)
    if event is None:
        return HttpResponse(status=400)

    payment.handle_stripe_webhook(event)
    return HttpResponse(status=200)


def _parse_stripe_payload(body: str) -> stripe.Event:
    # TODO: Verify signature
    # https://stripe.com/docs/webhooks/signatures
    try:
        data = json.loads(body)
    except ValueError:
        return None
    try:
        return stripe.Event.construct_from(data, stripe.api_key)
    except ValueError as e:
        logger.exception("Invalid Stripe payload! body=%s", data)
        return None


@transaction.atomic
def select_seats(request, show_slug):
    show = Show.objects.get(slug=show_slug)
    reservation = _get_or_create_reservation_object(request, show)

    taken_seats_qs = Reservation.active.exclude(pk=reservation.pk).filter(show=show)
    _set_session_timeout(request)

    seats_in_venue = Seat.objects.filter(group__venue=show.venue).all()
    available_seats = seats_in_venue.exclude(id__in=show.ticket_set.values_list('seat_id')).all()

    if request.POST:
        if show.free_seating:
            num_available_seats = available_seats.count()
            requested_normal_seats = int(request.POST.get('normal', 0))
            requested_student_seats = int(request.POST.get('student', 0))

            num_requested_seats = requested_student_seats + requested_normal_seats
            if num_requested_seats <= num_available_seats:
                student_seats = available_seats[0:requested_student_seats]
                normal_seats = available_seats[requested_student_seats:num_requested_seats]

                reservation.build_tickets(student=student_seats, normal=normal_seats)
                reservation.save()
                return redirect("booking_overview", show_slug=show.slug)
            else:
                messages.error(request, "Det finns inte tillräckligt många biljetter kvar.")

        else:
            # Select seats from seatmap
            seat_params = _seat_specifications(request)
            if not _all_seats_available(taken_seats_qs, seat_params.keys()):
                messages.error(request, "Vissa av platserna du valde har redan blivit bokade av någon annan")
            elif _some_seat_is_missing_ticket_type(seat_params):
                messages.error(request, "Du måste välja biljettyp för alla platser")
            else:
                reservation.tickets = seat_params
                reservation.save()
                return redirect("booking_overview", show_slug=show.slug)

    taken_seats = set(map(int, set().union(*[r.tickets.keys() for r in taken_seats_qs.all()])))

    pricings, seats = _build_pricings_and_seats(show.venue)
    if show.free_seating:
        pricings = next(iter(pricings.values()), {})

    return TemplateResponse(request, "ticket/select_seats.html", {
        'taken_seats': list(taken_seats),
        'show': show,
        'venue': show.venue,
        'pricings': pricings,
        'seats': json.dumps(seats),
        'num_available_seats': len(available_seats),
    })


@transaction.atomic
def booking_overview(request, show_slug):
    show = Show.objects.get(slug=show_slug)
    if _session_expired(request):
        messages.warning(request, "Du har väntat för länge, så din bokning har tröttnat och gått och lagt sig. Du får börja om från början!")
        return redirect("select_seats", show_slug=show_slug)

    _set_session_timeout(request)

    reservation = _get_or_create_reservation_object(request, show)
    if settings.PAYMENT_PROCESS == "stripe":
        payment_intent = payment.get_payment_intent_from_reservation(request, reservation)
    else:
        payment_intent = {"client_secret": "not_stripe"}

    if not reservation.tickets:
        messages.warning(request, "Du måste välja minst en plats")
        return redirect("select_seats", show_slug=show_slug)

    if show.free_seating:
        reserved_seats = {}
        for seat in reservation.seats():
            ticket_type = reservation.tickets[str(seat.id)]
            tickets = reserved_seats.get(ticket_type, {
                'price': seat.price_for_type(ticket_type),
                'count': 0,
                'group': seat.group.name,
            })
            tickets['count'] += 1
            reserved_seats[ticket_type] = tickets

        seats = [
            "%d x %s (à %dkr)" % (
                ticket_group['count'],
                ticket_group['group'],
                ticket_group['price'],
            )
            for (ticket_type, ticket_group) in reserved_seats.items()
        ]
        num_tickets = sum((group['count'] for (ticket_type, group) in reserved_seats.items()))
    else:
        reserved_seats = {seat.id: seat for seat in reservation.seats()}
        seats = [
            "%s: %s (%s, %dkr)" % (
                reserved_seats[int(id)].group.name,
                reserved_seats[int(id)].name,
                ticket_type,
                reserved_seats[int(id)].price_for_type(ticket_type)
            )
            for (id, ticket_type) in reservation.tickets.items()
        ]
        num_tickets = len(seats)

    return TemplateResponse(request, 'ticket/payment.html', {
        'seats': seats,
        'payment_partial': _payment_partial(reservation),
        'reservation': reservation,
        'stripe_payment_indent': payment_intent,
        'stripe_key': stripe_keys['publishable_key'],
        'num_tickets': num_tickets,
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
            payment.apply_voucher(request, reservation)
        except KeyError:
            messages.error(request, "För att kunna få rabatt måste du fylla i ett presentkort")
        except InvalidVoucherException:
            messages.error(request, "Presentkortet har redan använts")
        except AlreadyDiscountedException:
            messages.error(request, "Du har redan använt ett presentkort")
        except Voucher.DoesNotExist:
            messages.error(request, "Ogiltigt presentkort")

    return redirect("booking_overview", show_slug=show.slug)


@require_POST
def process_payment(request, reservation_id):
    reservation = Reservation.objects.get(pk=reservation_id)

    if _session_expired(request):
        messages.warning(request, "Du har väntat för länge, så din bokning har tröttnat och gått och lagt sig. Du får börja om från början!")
        return redirect("select_seats", show_slug=reservation.show.slug)

    if not reservation.is_free() and settings.PAYMENT_PROCESS == "stripe":
        # We should only end up here if the tickets are free,
        # since otherwise we want to handle the flow using stripe webhooks
        messages.error(request, "Något gick fel i betalningen.")
        return redirect("booking_overview", show_slug=reservation.show.slug)

    billing_data = request.POST
    reference = request.POST.get("reference", "")
    payment.handle_successful_payment(reservation, billing_data, reference)
    return redirect("reservation_detail", reservation_code=reservation.reservation_code)


def reservation_detail(request, reservation_code):
    reservation = Reservation.objects.get(reservation_code=reservation_code)
    email_form = CustomerEmailForm()

    return TemplateResponse(request, "reservation_detail.html", {
        'reservation': reservation,
        'show': reservation.show,
        'venue': reservation.show.venue,
        'production': reservation.show.production,
        'tickets': reservation.ticket_set(),
        'email_form': email_form,
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
    }, content_type="utf-8").render()

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


@require_POST
def cancel_reservation(request, show_id):
    reservation_id = request.session.pop(f"show_{show_id}", None)
    request.session.pop("reservation_timeout", None)
    request.session.pop("payment_intent_id", None)

    Reservation.objects.filter(pk=reservation_id).delete()
    return redirect("ticket_home")


@require_POST
def send_reservation_email(request, reservation_code):
    reservation = get_object_or_404(Reservation, reservation_code=reservation_code)
    form = CustomerEmailForm(data=request.POST)
    if form.is_valid():
        send_ticket_email_to_customer(reservation, form.data['email'])
        messages.success(request, 'E-postmeddelande skickat!')
    else:
        messages.error(request, 'Felaktig e-postadress')

    return redirect("reservation_detail", reservation_code=reservation.reservation_code)


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
            reservation = Reservation.objects.get(pk=reservation_id, finalized=False)
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
        seat.replace("seat_", ""): ticket_type
        for seat, ticket_type in request.POST.items()
        if seat.startswith("seat_")
    }


def _some_seat_is_missing_ticket_type(seat_params):
    return any(not ticket_type for (seat, ticket_type) in seat_params.items())


def _build_pricings_and_seats(venue):
    qs = PricingModel.objects.select_related('seating_group').filter(seating_group__venue_id=venue)
    pricings = {
        pricing.seating_group_id: pricing.prices
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
