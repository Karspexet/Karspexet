# coding: utf-8
from django.core import mail
import pytest
import stripe
from django.utils import timezone

from factories import factories as f
from factories.fixtures import show  # noqa
from karspexet.ticket.models import Seat, Ticket
from karspexet.ticket.payment import handle_successful_payment


@pytest.mark.django_db
def test_handle_successful_payment(show):
    seat = Seat.objects.first()
    tickets = {str(seat.id): "normal"}
    reservation = f.CreateReservation(
        tickets=tickets, session_timeout=timezone.now(), show=show
    )

    event = _stripe_event()
    payment = event.data.object
    payment.metadata["reservation_id"] = str(reservation.id)
    handle_successful_payment(payment)

    reservation.refresh_from_db()
    assert reservation.finalized

    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == ["Agata <agata.christie@example.com>"]

    assert Ticket.objects.count() == 1


def _stripe_event():
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
                "metadata": {},
                "next_action": None,
                "object": "payment_intent",
                "on_behalf_of": None,
                "payment_method": "pm_1FmmIZHLvgPvarOiI710yOuB",
                "payment_method_options": {
                    "card": {
                        "installments": None,
                        "request_three_d_secure": "automatic",
                    }
                },
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
