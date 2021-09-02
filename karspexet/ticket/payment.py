from __future__ import annotations

import logging

import stripe
from django.conf import settings

from karspexet.ticket.models import Account, Reservation, Ticket
from karspexet.ticket.tasks import send_ticket_email_to_customer
from karspexet.venue.models import Seat

logger = logging.getLogger(__name__)
stripe.api_key = settings.STRIPE_SECRET_KEY


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

        reservation_id = payment_intent.metadata["reservation_id"]
        try:
            reservation = Reservation.objects.get(id=reservation_id)
        except Reservation.DoesNotExist:
            # This is not an error we can recover from, so let's log the error and return 200 OK :(
            logger.error("Payment succeeded for missing Reservation=%s", reservation_id, extra={
                "payment": payment_intent,
            })
            return

        charge = payment_intent.charges.data[0]
        billing_details = charge.billing_details
        reference = get_reference_from_payment(charge.payment_method)

        handle_successful_payment(reservation, billing_details, reference)
        logger.info("PaymentIntent=%s for Reservation=%s succeeded", payment_intent.id, reservation.id)


def get_reference_from_payment(payment_method_id):
    try:
        return stripe.PaymentMethod.retrieve(payment_method_id).metadata.get("reference", "")
    except stripe.error.StripeError:
        # TODO: Better handling of error? Should we store payment_method_id instead?
        logger.exception("Failed to get reference from payment_method")
        return None


def handle_successful_payment(reservation: Reservation, billing_data: dict, reference=""):
    """
    Our honored customer has paid us money - let's send them a ticket
    """
    if reservation.finalized:
        return

    billing = _pick(billing_data, ["name", "phone", "email"])
    account = Account.objects.filter(**billing).first()
    if account is None:
        account = Account.objects.create(**billing)

    for seat_id, ticket_type in reservation.tickets.items():
        seat = Seat.objects.get(pk=seat_id)
        ticket = Ticket.objects.create(
            price=seat.price_for_type(ticket_type),
            ticket_type=ticket_type,
            show=reservation.show,
            seat=seat,
            account=account,
            reference=reference
        )

    reservation.finalized = True
    reservation.save()

    send_ticket_email_to_customer(reservation, account.email, account.name)


def _pick(data: dict, fields: list[str]) -> dict[str, str]:
    return {f: data.get(f, "") or "" for f in fields}
