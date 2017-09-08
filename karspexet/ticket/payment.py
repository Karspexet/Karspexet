import stripe
import logging

from django.conf import settings
from django.core.mail import send_mail
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

logger = logging.getLogger(__file__)
stripe_keys = settings.ENV["stripe"]
stripe.api_key = stripe_keys['secret_key']

class PaymentError(Exception):
    pass


class PaymentProcess:
    def __init__(self, reservation, post_data):
        self.reservation = reservation
        self.data = post_data

    def run(reservation, post_data):
        if settings.PAYMENT_PROCESS == "fake":
            process_class = FakePaymentProcess
        elif settings.PAYMENT_PROCESS == "stripe":
            process_class = StripePaymentProcess
        else:
            raise TypeError(
                "Invalid payment process setting {}. "
                "Please use either 'stripe' or 'fake'".format(settings.PAYMENT_PROCESS)
            )

        return process_class(reservation, post_data).process()

    @transaction.atomic
    def process(self):
        self.account = self._create_account()
        self._charge_card()

        tickets = self._create_tickets()
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
        subject = "Dina biljetter till Kårspexet"
        body = """
        Här är dina biljetter till Kårspexets föreställning: %s
        """ % (self.reservation.show)
        to_address = "%s <%s>" % (self.account.name, self.account.email)
        send_mail(
            subject,
            body,
            'noreply@karspexet.se',
            [to_address],
            fail_silently=False,
        )

class FakePaymentProcess(PaymentProcess):
    def _charge_card(self):
        if self.data['payment_success'] == 'true':
            return True
        else:
            raise PaymentError("NO TICKETS FOR YOU")


class StripePaymentProcess(PaymentProcess):
    def _charge_card(self):
        amount = self.reservation.total_price() * 100 # Öre
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
