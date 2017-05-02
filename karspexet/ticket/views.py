from dateutil.relativedelta import relativedelta
from dateutil import parser
from django.shortcuts import render, redirect
from django.forms.formsets import formset_factory
from django.utils import timezone
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

from karspexet.show.models import Show
from karspexet.venue.models import Seat
from karspexet.ticket.models import Reservation
from karspexet.ticket.forms import TicketTypeForm, SeatingGroupFormSet

import stripe
from django.conf import settings

stripe_keys = settings.ENV["stripe"]

stripe.api_key = stripe_keys['secret_key']

SESSION_TIMEOUT_MINUTES = 30


def home(request):
    upcoming_shows = Show.upcoming()

    return render(request, "home.html", {
        'upcoming_shows': upcoming_shows
    })


def select_seats(request, show_id):
    show = Show.objects.get(id=show_id)
    reservation = _get_or_create_reservation_object(request, show)
    taken_seats_qs = Reservation.active.exclude(pk=reservation.pk).filter(show=show)
    _set_session_timeout(request)

    if request.POST:
        seat_params = _seat_specifications(request)
        if _all_seats_available(taken_seats_qs, seat_params.keys()):
            reservation.tickets = seat_params
            reservation.save()
            return redirect("payment", show_id=show_id)
        else:
            messages.error(request, "Some of your chosen seats are already taken")

    taken_seats = set(map(int,set().union(*[r.tickets.keys() for r in taken_seats_qs.all()])))
    forms = [
        SeatingGroupFormSet(seating_group, taken_seats)
        for seating_group
        in show.venue.seatinggroup_set.all()
    ]

    return render(request, "select_seats.html", {
        'show': show,
        'venue': show.venue,
        'forms': forms,
    })

def payment(request, show_id):
    if _session_expired(request):
        messages.warning(request, "Your session has expired. Please start over from scratch.")
        return redirect("select_seats", show_id=show_id)

    _set_session_timeout(request)
    show = Show.objects.get(pk=show_id)
    reservation = _get_or_create_reservation_object(request, show)
    seats = Seat.objects.filter(pk__in=reservation.tickets.keys())

    return render(request, 'payment.html', {
        'show': show,
        'seats': seats,
        'reservation': reservation,
        'stripe_key': stripe_keys['publishable_key'],
    })

@transaction.atomic
def process_payment(request, reservation_id):
    # TODO:
    # * create account/customer object
    # * create ticket objects
    # * send email to customer

    reservation = Reservation.objects.get(pk=reservation_id)

    if _session_expired(request):
        messages.warning(request, "Your session has expired. Please start over from scratch.")
        return redirect("select_seats", show_id=reservation.show_id)

    if request.POST:
        amount = reservation.total_price() * 100 # Öre

        stripe_token_type = request.POST['stripeTokenType']
        stripe_email = request.POST['stripeEmail']
        stripe_token = request.POST['stripeToken']

        customer = stripe.Customer.create(
            email=stripe_email,
            source=stripe_token
        )
        charge = stripe.Charge.create(
            customer=customer.id,
            amount=amount,
            currency="sek",
            description="Biljetter till Kårspexet"
        )

        reservation.finalized = True
        reservation.save()
        request.session['reservation_timeout'] = None
        request.session['reservation_id'] = None

        return render(request, 'payment_succeeded.html', {
            'reservation': reservation,
        })


    pass


def _session_expired(request):
    timeout = request.session.get('reservation_timeout', None)
    if timeout:
        timeout = parser.parse(timeout)
        return timeout < timezone.now()

def _set_session_timeout(request):
    request.session['reservation_timeout'] = (timezone.now() + relativedelta(minutes=SESSION_TIMEOUT_MINUTES)).isoformat()

def _get_or_create_reservation_object(request, show):
    timeout = timezone.now() + relativedelta(minutes=SESSION_TIMEOUT_MINUTES)

    if request.session.get('reservation_id'):
        try:
            reservation = Reservation.objects.get(pk=request.session['reservation_id'], show=show)
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
