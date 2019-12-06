# coding: utf-8

import logging

import stripe
from django.conf import settings
from django.db import transaction
from stripe.error import APIConnectionError, AuthenticationError, InvalidRequestError, RateLimitError, StripeError

from karspexet.ticket.models import Account, Reservation, Ticket
from karspexet.ticket.tasks import send_ticket_email_to_customer
from karspexet.venue.models import Seat

logger = logging.getLogger(__name__)
stripe_keys = settings.ENV["stripe"]
stripe.api_key = stripe_keys['secret_key']


class PaymentError(Exception):
    pass


class PaymentProcess:
    def __init__(self, reservation, post_data, request):
        self.reservation = reservation
        self.data = post_data
        self.request = request

    def run(reservation, post_data, request):
        if settings.PAYMENT_PROCESS == "fake":
            process_class = FakePaymentProcess
        elif settings.PAYMENT_PROCESS == "stripe":
            process_class = StripePaymentProcess
        else:
            raise TypeError(
                "Invalid payment process setting {}. "
                "Please use either 'stripe' or 'fake'".format(settings.PAYMENT_PROCESS)
            )

        try:
            return process_class(reservation, post_data, request).process()
        except OSError as error:
            logger.exception("OSError in payment process", exc_info=True, extra={
                'request': request
            })
            raise PaymentError("OSError in payment process")

    @transaction.atomic
    def process(self):
        assert self.reservation.tickets, "A reservation must have tickets to be paid for (reservation_id=%d)" % self.reservation.id

        self.account = self._create_account()
        self._create_tickets()

        # Here we ensure that the ticket_price and total on the reservatino are populated.
        # This _should_ be done in Reservation.save, but we can afford a few CPU cycles to know that this happens.
        self.reservation.calculate_ticket_price_and_total()
        if self.reservation.total > 0:
            self._charge_card()

        self.reservation = self._finalize_reservation()
        self._send_mail_to_customer()

        return self.reservation

    def _create_account(self):
        email = self.data['email']
        phone = self.data['phone']
        name = self.data['name']

        return Account.objects.create(
            name=name,
            phone=phone,
            email=email
        )

    def _charge_card(self):
        raise NotImplementedError

    def _create_tickets(self):
        tickets = []
        for seat_id, ticket_type in self.reservation.tickets.items():
            seat = Seat.objects.get(pk=seat_id)
            tickets.append(
                Ticket.objects.create(
                    price=seat.price_for_type(ticket_type),
                    ticket_type=ticket_type,
                    show=self.reservation.show,
                    seat=seat,
                    account=self.account
                )
            )

        return tickets

    def _finalize_reservation(self):
        self.reservation.finalized = True
        self.reservation.save()

        return self.reservation

    def _send_mail_to_customer(self):
        return send_ticket_email_to_customer(self.reservation, self.account.email, self.account.name)


class FakePaymentProcess(PaymentProcess):
    def _charge_card(self):
        if self.data['payment_success'] == 'true':
            return True
        else:
            raise PaymentError("NO TICKETS FOR YOU")


class StripePaymentProcess(PaymentProcess):
    def _charge_card(self):
        assert self.reservation.total > 0, "We cannot charge a reservation without a total price"
        amount = self.reservation.total * 100  # Öre
        stripe_token = self.data['stripeToken']

        try:
            return stripe.Charge.create(
                source=stripe_token,
                amount=amount,
                currency="sek",
                description="Biljetter till Kårspexet"
            )
        except (APIConnectionError, AuthenticationError, InvalidRequestError, RateLimitError, StripeError) as error:
            logger.error(error)
            raise PaymentError from error


def get_payment_intent_from_reservation(reservation):
    return stripe.PaymentIntent.create(
        amount=reservation.get_amount(),
        currency="sek",
        payment_method_types=["card"],
        idempotency_key=str(reservation.id),
        statement_descriptor="Biljett Kårspexet",
        metadata={"reservation_id": reservation.id,},
    )


def handle_stripe_webhook(event: stripe.Event):
    logger.info("Stripe Event: %r", event)

    handled = False
    payment_intent: stripe.PaymentIntent
    if event.type == "payment_intent.created":
        payment_intent = event.data.object
        logger.info("PaymentIntent created: %s", payment_intent.id)
        handled = True

    elif event.type == "payment_intent.payment_failed":
        payment_intent = event.data.object
        logger.info("PaymentIntent failed: %s", payment_intent.id)
        handled = True

    elif event.type == "payment_intent.succeeded":
        payment_intent = event.data.object
        handle_successful_payment(payment_intent)
        logger.info("PaymentIntent succeeded: %s", payment_intent.id)
        handled = True

    else:
        logger.warning("Unexpected event type: %s", event.type)

    return handled


def handle_successful_payment(payment: stripe.PaymentIntent):
    """
    Our honored customer has paid us money - let's send them a ticket
    """
    reservation_id = payment.metadata["reservation_id"]
    reservation: Reservation = Reservation.objects.get(id=reservation_id)

    billing_details = payment.charges.data[0].billing_details
    billing = _pick(billing_details, ["name", "phone", "email"])

    account = Account.objects.create(**billing)

    tickets = []
    for seat_id, ticket_type in reservation.tickets.items():
        seat = Seat.objects.get(pk=seat_id)
        ticket = Ticket.objects.create(
            price=seat.price_for_type(ticket_type),
            ticket_type=ticket_type,
            show=reservation.show,
            seat=seat,
            account=account,
        )
        tickets.append(ticket)

    reservation.finalized = True
    reservation.save()

    send_ticket_email_to_customer(reservation, account.email, account.name)


def _pick(data, fields):
    return {f: data[f] for f in fields}
