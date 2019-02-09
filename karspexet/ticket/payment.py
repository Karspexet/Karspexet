# coding: utf-8

import stripe
import logging

from django.conf import settings
from django.db import transaction
from stripe.error import (
    APIConnectionError,
    AuthenticationError,
    InvalidRequestError,
    RateLimitError,
    StripeError
)

from karspexet.ticket.models import Account, Ticket
from karspexet.venue.models import Seat
from karspexet.ticket.tasks import send_ticket_email_to_customer

logger = logging.getLogger(__file__)
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
        amount = self.reservation.total * 100 # Öre
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
