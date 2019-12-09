# coding: utf-8

import logging

import stripe
from django.conf import settings

from karspexet.ticket.models import Account, Reservation, Ticket
from karspexet.ticket.tasks import send_ticket_email_to_customer
from karspexet.venue.models import Seat

logger = logging.getLogger(__name__)
stripe_keys = settings.ENV["stripe"]
stripe.api_key = stripe_keys["secret_key"]


def get_payment_intent_from_reservation(request, reservation):
    payment_intent_id = request.session.get("payment_intent_id")
    if payment_intent_id:
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        if intent.metadata.reservation_id == str(reservation.id):
            amount = reservation.get_amount()
            if amount > 0 and intent.amount != amount:
                logger.info("Updated PaymentIntent=%s for reservation=%s", intent.id, reservation.id)
                return stripe.PaymentIntent.modify(payment_intent_id, amount=amount)
            return intent

        # We have a PaymentIntent from an old reservation in the session - create a new one instead
        logger.warning("Retrieved wrong PaymentIntent=%s for reservation=%s", intent.id, reservation.id)

    intent = stripe.PaymentIntent.create(
        amount=reservation.get_amount(),
        currency="sek",
        payment_method_types=["card"],
        idempotency_key=str(reservation.id),
        statement_descriptor="Biljett Kårspexet",
        metadata={"reservation_id": reservation.id},
    )
    logger.info("Created PaymentIntent=%s for reservation=%s", intent.id, reservation.id)
    request.session["payment_intent_id"] = intent.id
    return intent


def apply_voucher(request, reservation):
    # Since we have a reservation, we can assume there is also a PaymentIntent created
    payment_intent_id = request.session["payment_intent_id"]
    code = request.POST["voucher_code"]
    reservation.apply_voucher(code)
    reservation.save()
    new_amount = reservation.get_amount()
    if not new_amount:
        stripe.PaymentIntent.cancel(payment_intent_id)
    else:
        stripe.PaymentIntent.modify(payment_intent_id, amount=new_amount)


def handle_stripe_webhook(event: stripe.Event):
    logger.info("Stripe Event: %r", event)

    if event.type == "payment_intent.succeeded":
        payment_intent: stripe.PaymentIntent = event.data.object

        reservation = Reservation.objects.get(id=payment_intent.metadata["reservation_id"])
        billing_details = payment_intent.charges.data[0].billing_details

        handle_successful_payment(reservation, billing_details)
        logger.info("PaymentIntent=%s for Reservation=%s succeeded", payment_intent.id, reservation.id)


def handle_successful_payment(reservation: Reservation, billing_data: dict):
    """
    Our honored customer has paid us money - let's send them a ticket
    """
    if reservation.finalized:
        return

    billing = _pick(billing_data, ["name", "phone", "email"])
    account = Account.objects.filter(**billing).first()
    if account is None:
        Account.objects.create(**billing)

    for seat_id, ticket_type in reservation.tickets.items():
        seat = Seat.objects.get(pk=seat_id)
        ticket = Ticket.objects.create(
            price=seat.price_for_type(ticket_type),
            ticket_type=ticket_type,
            show=reservation.show,
            seat=seat,
            account=account,
        )

    reservation.finalized = True
    reservation.save()

    send_ticket_email_to_customer(reservation, account.email, account.name)


def _pick(data, fields):
    return {f: data.get(f, "") for f in fields}
