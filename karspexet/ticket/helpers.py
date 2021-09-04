from __future__ import annotations

from dateutil import parser
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

from karspexet.ticket.models import PricingModel, Reservation
from karspexet.venue.models import Seat

SESSION_TIMEOUT_MINUTES = 30


def session_expired(request) -> bool:
    timeout = request.session.get("reservation_timeout", None)
    if timeout:
        timeout = parser.parse(timeout)
        return timeout < timezone.now()
    return False


def set_session_timeout(request) -> None:
    timeout_at = timezone.now() + relativedelta(minutes=SESSION_TIMEOUT_MINUTES)
    request.session["reservation_timeout"] = timeout_at.isoformat()


def get_or_create_reservation_object(request, show) -> Reservation:
    timeout = timezone.now() + relativedelta(minutes=SESSION_TIMEOUT_MINUTES)
    session_key = f"show_{show.id}"
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


def all_seats_available(qs, seat_ids) -> bool:
    return not qs.filter(tickets__has_any_keys=seat_ids).exists()


def seat_specifications(request) -> dict:
    return {
        seat.replace("seat_", ""): ticket_type
        for seat, ticket_type in request.POST.items()
        if seat.startswith("seat_")
    }


def some_seat_is_missing_ticket_type(seat_params) -> bool:
    return any(not ticket_type for (seat, ticket_type) in seat_params.items())


def build_pricings_and_seats(venue) -> tuple[dict, dict]:
    qs = PricingModel.objects.select_related("seating_group").filter(seating_group__venue_id=venue)
    pricings = {pricing.seating_group_id: pricing.prices for pricing in qs.all()}

    seats = {
        "seat-%d" % s.id: {"id": s.id, "name": s.name, "group": s.group_id}
        for s in Seat.objects.filter(group_id__in=pricings.keys())
    }

    return (pricings, seats)


def payment_partial(reservation) -> str:
    if reservation.total == 0:
        return "_discount_payment.html"
    if settings.PAYMENT_PROCESS == "stripe":
        return "_stripe_payment.html"
    else:
        return "_fake_payment.html"


def get_used_seats(reservation: Reservation) -> list[tuple[str, str, int]]:
    seats: list[tuple[str, str, int]] = []
    if reservation.show.free_seating:
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
    return seats
