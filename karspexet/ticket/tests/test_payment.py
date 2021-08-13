from unittest import mock

import pytest
import stripe
from django.contrib.sessions.middleware import SessionMiddleware
from django.core import mail
from django.shortcuts import reverse
from django.test import RequestFactory
from django.utils import timezone

from factories import factories as f
from karspexet.ticket import views
from karspexet.ticket.models import Reservation, Seat, Ticket
from karspexet.ticket.payment import (get_payment_intent_from_reservation, handle_stripe_webhook,
                                      handle_successful_payment)


@pytest.mark.django_db
class TestPaymentSuccess:
    def test_handle_success_webhook(self, show):
        reservation = self._build_reservation(show)
        intent = FakeIntent(reservation)

        with mock.patch("karspexet.ticket.payment.stripe") as mock_stripe:
            mock_stripe.PaymentMethod.retrieve.return_value = intent
            handle_stripe_webhook(_stripe_event(metadata={"reservation_id": reservation.id}))
        reservation.refresh_from_db()
        assert reservation.finalized

    def test_handle_missing_reservations_without_crashing(self, show):
        r_id = 1
        assert not Reservation.objects.filter(id=r_id).exists()
        handle_stripe_webhook(_stripe_event(metadata={"reservation_id": r_id}))

    def test_is_idempotent(self, show):
        reservation = self._build_reservation(show)
        data = {
            "name": "Frank Hamer",
            "email": "frank@hamer.com",
            "profession": "Police Inspector, Adventurer, Author",
        }
        # Handle the same webhook twice to make sure we handle it idempotently
        handle_successful_payment(reservation, data)
        handle_successful_payment(reservation, data)

        reservation.refresh_from_db()
        assert reservation.finalized

        assert len(mail.outbox) == 1
        assert mail.outbox[0].to == ["Frank Hamer <frank@hamer.com>"]

        assert Ticket.objects.count() == 1

    @mock.patch("karspexet.ticket.payment.send_ticket_email_to_customer", autospec=True, side_effect=Exception)
    def test_finalizes_reservation_even_with_email_error(self, _, show):
        reservation = self._build_reservation(show)
        with pytest.raises(Exception):
            handle_successful_payment(reservation, {"name": "mayor", "email": "mayor"})
        reservation.refresh_from_db()
        assert reservation.finalized

    def _build_reservation(self, show):
        seat = Seat.objects.first()
        tickets = {str(seat.id): "normal"}
        return f.CreateReservation(tickets=tickets, session_timeout=timezone.now(), show=show)

    def test_stores_reference_if_passed(self, show):
        reservation = self._build_reservation(show)
        data = {
            "name": "Frank Hamer",
            "email": "frank@hamer.com",
            "profession": "Police Inspector, Adventurer, Author",
        }
        handle_successful_payment(reservation, data, reference="Hank Framer")
        assert Ticket.objects.first().reference == "Hank Framer"


@pytest.mark.django_db
class TestGetPaymentIntentFromReservation:
    def test_create_payment_intent_if_none_stored_in_session(self, show):
        reservation = self._build_reservation(show)
        intent = FakeIntent(reservation)
        request = self._build_request(reservation)

        with mock.patch("karspexet.ticket.payment.stripe") as mock_stripe:
            mock_stripe.PaymentIntent.create.return_value = intent
            intent = get_payment_intent_from_reservation(request, reservation)

        assert mock_stripe.PaymentIntent.create.called
        assert request.session["payment_intent_id"] == intent.id

    def test_retrieve_payment_intent_if_one_is_stored_in_session(self, show):
        reservation = self._build_reservation(show)
        intent = FakeIntent(reservation)
        request = self._build_request(reservation)
        request.session["payment_intent_id"] = intent.id

        with mock.patch("karspexet.ticket.payment.stripe") as mock_stripe:
            mock_stripe.PaymentIntent.retrieve.return_value = intent
            intent = get_payment_intent_from_reservation(request, reservation)

        assert mock_stripe.PaymentIntent.retrieve.called
        assert not mock_stripe.PaymentIntent.modify.called
        assert not mock_stripe.PaymentIntent.create.called
        assert request.session["payment_intent_id"] == intent.id

    def test_modify_payment_intent_if_reservation_amount_changed(self, show):
        reservation = self._build_reservation(show)
        intent = FakeIntent(reservation)

        another_seat = Seat.objects.all()[1]
        reservation.tickets[str(another_seat.id)] = "normal"
        reservation.save()
        updated_amount = reservation.get_amount()

        request = self._build_request(reservation)
        request.session["payment_intent_id"] = intent.id

        with mock.patch("karspexet.ticket.payment.stripe") as mock_stripe:
            mock_stripe.PaymentIntent.retrieve.return_value = intent
            mock_stripe.PaymentIntent.modify.return_value = intent
            intent = get_payment_intent_from_reservation(request, reservation)

        assert not mock_stripe.PaymentIntent.create.called
        mock_stripe.PaymentIntent.modify.assert_called_once_with(intent.id, amount=updated_amount)
        assert request.session["payment_intent_id"] == intent.id

    def test_change_payment_intent_if_incorrect_reservation_return(self, show):
        reservation_1 = self._build_reservation(show, seat=Seat.objects.all()[0])
        reservation_2 = self._build_reservation(show, seat=Seat.objects.all()[1])
        intent_1 = FakeIntent(reservation_1)
        intent_2 = FakeIntent(reservation_2)

        request = self._build_request(reservation_2)
        request.session["payment_intent_id"] = intent_1.id

        with mock.patch("karspexet.ticket.payment.stripe") as mock_stripe:
            mock_stripe.PaymentIntent.retrieve.return_value = intent_1
            mock_stripe.PaymentIntent.create.return_value = intent_2
            intent = get_payment_intent_from_reservation(request, reservation_2)

        mock_stripe.PaymentIntent.retrieve.assert_called_once_with(intent_1.id)
        assert not mock_stripe.PaymentIntent.modify.called
        assert mock_stripe.PaymentIntent.create.called
        assert request.session["payment_intent_id"] == intent.id

    def _build_reservation(self, show, seat=None):
        if seat is None:
            seat = Seat.objects.first()
        tickets = {str(seat.id): "normal"}
        return f.CreateReservation(tickets=tickets, session_timeout=timezone.now(), show=show)

    def _build_request(self, reservation):
        show = reservation.show
        url = reverse(views.booking_overview, args=[show.id])
        request = RequestFactory().post(url)
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()
        request.session[f"show_{show.id}"] = reservation.id

        return request


class FakeIntent:
    class Metadata:
        reservation_id = ""

        def get(self, key, default):
            return getattr(self, key, default)

    def __init__(self, reservation: Reservation) -> None:
        self.id = "fake_payment_intent_id_%s" % reservation.id
        self.amount = reservation.get_amount()
        self.metadata = self.Metadata()
        self.metadata.reservation_id = str(reservation.id)
        self.status = "pending"


def _stripe_event(metadata={}):
    data = {
        "api_version": "2019-12-03",
        "created": 1575659828,
        "data": {
            "object": {
                "amount": 1099,
                "amount_capturable": 0,
                "amount_received": 1099,
                "application": None,
                "application_fee_amount": None,
                "canceled_at": None,
                "cancellation_reason": None,
                "capture_method": "automatic",
                "charges": {
                    "data": [
                        {
                            "amount": 1099,
                            "amount_refunded": 0,
                            "application": None,
                            "application_fee": None,
                            "application_fee_amount": None,
                            "balance_transaction": "txn_foo",
                            "billing_details": {
                                "address": {
                                    "city": None,
                                    "country": None,
                                    "line1": None,
                                    "line2": None,
                                    "postal_code": None,
                                    "state": None,
                                },
                                "name": "Agata",
                                "email": "agata.christie@example.com",
                                "phone": "+44 123 456",
                            },
                            "captured": True,
                            "created": 1575659827,
                            "currency": "sek",
                            "customer": None,
                            "description": None,
                            "destination": None,
                            "dispute": None,
                            "disputed": False,
                            "failure_code": None,
                            "failure_message": None,
                            "fraud_details": {},
                            "id": "ch_1foo",
                            "invoice": None,
                            "livemode": False,
                            "metadata": {},
                            "object": "charge",
                            "on_behalf_of": None,
                            "order": None,
                            "outcome": {
                                "network_status": "approved_by_network",
                                "reason": None,
                                "risk_level": "normal",
                                "risk_score": 8,
                                "seller_message": "Payment complete.",
                                "type": "authorized",
                            },
                            "paid": True,
                            "payment_intent": "pi_1foo",
                            "payment_method": "pm_1foo",
                            "payment_method_details": {
                                "card": {
                                    "brand": "visa",
                                    "checks": {
                                        "address_line1_check": None,
                                        "address_postal_code_check": None,
                                        "cvc_check": "pass",
                                    },
                                    "country": "US",
                                    "exp_month": 4,
                                    "exp_year": 2024,
                                    "fingerprint": "foo",
                                    "funding": "credit",
                                    "installments": None,
                                    "last4": "4242",
                                    "network": "visa",
                                    "three_d_secure": None,
                                    "wallet": None,
                                },
                                "type": "card",
                            },
                            "receipt_email": None,
                            "receipt_number": None,
                            "receipt_url": "https://pay.stripe.com/receipts/foo/ch_1foo/rcpt_foo",
                            "refunded": False,
                            "refunds": {},
                            "review": None,
                            "shipping": None,
                            "source": None,
                            "source_transfer": None,
                            "statement_descriptor": "Biljett Karspexet",
                            "statement_descriptor_suffix": None,
                            "status": "succeeded",
                            "transfer_data": None,
                            "transfer_group": None,
                        }
                    ],
                    "has_more": False,
                    "object": "list",
                    "total_count": 1,
                    "url": "/v1/charges?payment_intent=pi_1foo",
                },
                "client_secret": "pi_1foo",
                "confirmation_method": "automatic",
                "created": 1575659813,
                "currency": "sek",
                "customer": None,
                "description": None,
                "id": "pi_1foo",
                "invoice": None,
                "last_payment_error": None,
                "livemode": False,
                "metadata": metadata,
                "next_action": None,
                "object": "payment_intent",
                "on_behalf_of": None,
                "payment_method": "pm_1FmmIZHLvgPvarOiI710yOuB",
                "payment_method_options": {"card": {"installments": None, "request_three_d_secure": "automatic"}},
                "payment_method_types": ["card"],
                "receipt_email": None,
                "review": None,
                "setup_future_usage": None,
                "shipping": None,
                "source": None,
                "statement_descriptor": "Biljett Karspexet",
                "statement_descriptor_suffix": None,
                "status": "succeeded",
                "transfer_data": None,
                "transfer_group": None,
            }
        },
        "id": "evt_1foo",
        "livemode": False,
        "object": "event",
        "pending_webhooks": 2,
        "request": {"id": "req_e7t54xKdbZkLJD", "idempotency_key": None},
        "type": "payment_intent.succeeded",
    }
    return stripe.Event.construct_from(data, "foo")
