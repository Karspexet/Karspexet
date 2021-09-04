from __future__ import annotations

import json
import logging

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
from karspexet.ticket.forms import ContactDetailsForm, CustomerEmailForm
from karspexet.ticket.models import (TICKET_TYPES, AlreadyDiscountedException, InvalidVoucherException, PricingModel,
                                     Reservation, Voucher)
from karspexet.ticket.tasks import send_ticket_email_to_customer
from karspexet.ticket.utils import qr_code_as_png_data_url
from karspexet.venue.models import Seat

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


def show_redirect(request, show_id: int):
    return redirect("select_seats", show_id=show_id)


@transaction.atomic
def select_seats(request, show_id: int):
    show: Show = get_object_or_404(Show, id=show_id)
    reservation = _get_or_create_reservation_object(request, show)

    taken_seats_qs = Reservation.active.exclude(pk=reservation.pk).filter(show=show)
    _set_session_timeout(request)

    seats_in_venue = Seat.objects.filter(group__venue=show.venue).all()
    available_seats = list(seats_in_venue.exclude(id__in=show.ticket_set.values_list('seat_id')).all())

    contact_form = ContactDetailsForm(data=request.POST or None)

    if request.POST:
        if contact_form.is_valid():
            request.session["contact_details"] = contact_form.cleaned_data

        if show.free_seating:
            prices = [t[0] for t in TICKET_TYPES]
            requested_seats: dict = {
                price: int(request.POST.get(price, 0)) for price in prices
            }
            num_requested_seats = sum(requested_seats.values())
            if num_requested_seats <= len(available_seats):
                seats = {}
                idx = 0
                for price, num_seats in requested_seats.items():
                    seats[price] = available_seats[idx:idx + num_seats]
                    idx += num_seats

                reservation.build_tickets(seats)
                reservation.save()
                return redirect("booking_overview", show_id=show.id)
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
                return redirect("booking_overview", show_id=show.id)

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
def booking_overview(request, show_id: int):
    show: Show = get_object_or_404(Show, id=show_id)
    if _session_expired(request):
        messages.warning(
            request, "Du har väntat för länge, så din bokning har tröttnat och gått och lagt sig. Du får börja om från början!")
        return redirect("select_seats", show_id=show.id)

    _set_session_timeout(request)

    reservation = _get_or_create_reservation_object(request, show)
    payment_intent = payment.get_payment_intent_from_reservation(request, reservation)

    if not reservation.tickets:
        messages.warning(request, "Du måste välja minst en plats")
        return redirect("select_seats", show_id=show.id)

    seats: list[tuple[str, str, int]] = []
    if show.free_seating:
        reserved_seats: dict = {}
        for seat in reservation.seats():
            ticket_type = reservation.tickets[str(seat.id)]
            tickets = reserved_seats.get(ticket_type, {
                'price': seat.price_for_type(ticket_type),
                'count': 0,
                'group': seat.group.name,
            })
            tickets['count'] += 1
            reserved_seats[ticket_type] = tickets

        for (ticket_type, ticket_group) in reserved_seats.items():
            seats.append((
                "%d x %s" % (ticket_group['count'], ticket_group['group']),
                ticket_type,
                ticket_group['price'],
            ))
    else:
        reserved_seats = {seat.id: seat for seat in reservation.seats()}
        for (id, ticket_type) in reservation.tickets.items():
            seat = reserved_seats[int(id)]
            seats.append((
                "%s: %s" % (seat.group.name, seat.name),
                ticket_type,
                seat.price_for_type(ticket_type),
            ))

    contact_details = request.session.get("contact_details")

    return TemplateResponse(request, 'ticket/payment.html', {
        'seats': seats,
        'reservation': reservation,
        'payment_partial': _payment_partial(reservation),
        'contact_details': contact_details,
        'stripe_payment_indent': payment_intent,
        'stripe_key': settings.STRIPE_PUBLISHABLE_KEY,
    })


@transaction.atomic
def apply_voucher(request, reservation_id: int):
    reservation = Reservation.objects.get(pk=reservation_id)
    show = reservation.show

    if _session_expired(request):
        messages.warning(
            request, "Du har väntat för länge, så din bokning har tröttnat och gått och lagt sig. Du får börja om från början!")
        return redirect("select_seats", show_id=show.id)

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

    return redirect("booking_overview", show_id=show.id)


@require_POST
def process_payment(request, reservation_id: int):
    reservation = Reservation.objects.get(pk=reservation_id)

    if _session_expired(request):
        messages.warning(
            request, "Du har väntat för länge, så din bokning har tröttnat och gått och lagt sig. Du får börja om från början!")
        return redirect("select_seats", show_id=reservation.show.id)

    if not reservation.is_free() and settings.PAYMENT_PROCESS == "stripe":
        # We should only end up here if the tickets are free,
        # since otherwise we want to handle the flow using stripe webhooks
        messages.error(request, "Något gick fel i betalningen.")
        return redirect("booking_overview", show_id=reservation.show.id)

    billing_data = request.POST
    reference = request.POST.get("reference", "")
    payment.handle_successful_payment(reservation, billing_data, reference)
    return redirect("reservation_detail", reservation_code=reservation.reservation_code)


def reservation_detail(request, reservation_code: str):
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


def ticket_detail(request, reservation_id: int, ticket_code):
    reservation = Reservation.objects.get(pk=reservation_id)
    ticket = reservation.ticket_set().get(ticket_code=ticket_code)

    return TemplateResponse(request, "ticket_detail.html", {
        "reservation": reservation,
        "show": reservation.show,
        "venue": reservation.show.venue,
        "production": reservation.show.production,
        "ticket": ticket,
        "seat": ticket.seat,
        "qr_code": qr_code_as_png_data_url(request),
    })


def ticket_pdf(request, reservation_id: int, ticket_code):
    from xhtml2pdf import pisa

    reservation = Reservation.objects.get(pk=reservation_id)
    ticket = reservation.ticket_set().get(ticket_code=ticket_code)

    html = TemplateResponse(request, "ticket_detail.html", {
        "reservation": reservation,
        "show": reservation.show,
        "venue": reservation.show.venue,
        "production": reservation.show.production,
        "ticket": ticket,
        "seat": ticket.seat,
        "qr_code": qr_code_as_png_data_url(request),
    }, content_type="utf-8").render().content.decode()

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = "inline;filename=karspexet-bokning-{}-{}.pdf".format(reservation_id, ticket_code)
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        raise Exception(pisa_status)
    return response


@require_POST
def cancel_reservation(request, show_id: int):
    reservation_id = request.session.pop(f"show_{show_id}", None)
    request.session.pop("reservation_timeout", None)
    request.session.pop("payment_intent_id", None)

    Reservation.objects.filter(pk=reservation_id).delete()
    return redirect("ticket_home")


@require_POST
def send_reservation_email(request, reservation_code: str):
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
    request.session['reservation_timeout'] = (
        timezone.now() + relativedelta(minutes=SESSION_TIMEOUT_MINUTES)).isoformat()


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
