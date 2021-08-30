from unittest import mock

import pytest
from django.contrib.sessions.middleware import SessionMiddleware
from django.shortcuts import reverse
from django.test import RequestFactory, TestCase, override_settings
from django.utils import timezone

from factories import factories as f
from karspexet.ticket import views
from karspexet.ticket.models import Discount, Reservation, Seat, Voucher


class TestTicketViews(TestCase):
    def test_home_lists_visible_upcoming_shows(self):
        tomorrow = timezone.now() + timezone.timedelta(days=1)
        yesterday = timezone.now() - timezone.timedelta(days=1)

        show = f.CreateShow(date=tomorrow)
        old_show = f.CreateShow(date=yesterday)
        invisible_show = f.CreateShow(date=tomorrow, visible=False)

        response = _get(views.home)
        shows = response.context_data["upcoming_shows"]
        assert show in shows
        assert old_show not in shows
        assert invisible_show not in shows

    def test_select_seats(self):
        show = f.CreateShow(production__description="Uppsättningen")
        response = self.client.get(reverse(views.select_seats, args=[show.id]))
        self.assertContains(response, "Uppsättningen")


@pytest.mark.django_db
@override_settings(PAYMENT_PROCESS="stripe")
def test_booking_overview_with_active_session__includes_payment_intent(show, client):
    reservation = _reservation(show)
    session = client.session
    session["show_%s" % show.id] = str(reservation.id)
    session.save()

    url = reverse(views.booking_overview, args=[show.id])
    with mock.patch("karspexet.ticket.views.payment", autospec=True) as mock_payment:
        mock_payment_intent = object()
        mock_payment.get_payment_intent_from_reservation.return_value = mock_payment_intent
        response = client.get(url)
    assert response.status_code == 200
    assert response.context["reservation"] == reservation
    assert response.context["stripe_payment_indent"] == mock_payment_intent


@pytest.mark.django_db
@override_settings(PAYMENT_PROCESS="fake")
def test_booking_overview_with_active_session__with_fake_intent(show, client):
    reservation = _reservation(show)
    session = client.session
    session["show_%s" % show.id] = str(reservation.id)
    session.save()

    url = reverse(views.booking_overview, args=[show.id])
    with mock.patch("karspexet.ticket.views.payment", autospec=True):
        response = client.get(url)
    assert response.status_code == 200
    assert response.context["reservation"] == reservation
    assert "fake" in response.context["payment_partial"]


class TestWebhooks(TestCase):
    def test_stripe_webhooks(self):
        response = self._post(data="invalid")
        assert response.status_code == 400

        with mock.patch("karspexet.ticket.views.payment", autospec=True) as spy:
            response = self._post(data='{"type": "payment_intent.succeeded"}')
            spy.handle_stripe_webhook.assert_called_once()
        assert response.status_code == 200

        response = self._post(data='{"type": "unknown"}')
        assert response.status_code == 200

    def _post(self, data):
        url = reverse(views.stripe_webhooks)
        return self.client.post(url, data=data, content_type="application/json")


@pytest.mark.django_db
def test_apply_voucher_with_active_reservation__updates_reservation_total(client, show):
    reservation = _reservation(show)
    voucher = f.CreateVoucher()
    session = client.session
    session["show_%s" % show.id] = str(reservation.id)
    session["payment_intent_id"] = "1"
    session.save()

    assert reservation.total == 250

    url = reverse(views.apply_voucher, args=[reservation.id])
    with mock.patch("karspexet.ticket.payment.stripe", autospec=True) as mock_stripe:
        response = client.post(url, data={"voucher_code": voucher.code})
    assert response.status_code == 302
    assert mock_stripe.mock_calls == [mock.call.PaymentIntent.modify("1", amount=15000)]

    reservation.refresh_from_db()
    assert reservation.total == 150


@pytest.mark.django_db
def test_process_payment(client, show):
    reservation = _reservation(show)
    voucher = f.CreateVoucher(amount=reservation.total)
    discount = reservation.apply_voucher(voucher.code)
    reservation.save()
    assert reservation.is_free()

    url = reverse(views.process_payment, args=[reservation.id])
    response = client.post(url)
    assert response.status_code == 302
    assert response["Location"] == reverse(views.reservation_detail, args=[reservation.reservation_code])

    assert Reservation.objects.get(pk=reservation.id).finalized


@pytest.mark.django_db
def test_cancelling_a_discounted_reservation_allows_voucher_for_reuse(show, user):
    reservation = _reservation(show)
    voucher = Voucher.objects.create(amount=100, created_by=user)
    discount = reservation.apply_voucher(voucher.code)

    response = _post(views.cancel_reservation, show.id, session={f"show_{show.id}": reservation.id})

    assert Reservation.objects.filter(pk=reservation.id).count() == 0
    assert Discount.objects.filter(pk=discount.id).count() == 0


@pytest.mark.django_db
class TestSelectSeats:
    def test_creates_reservation_and_redirects_to_booking_overview(self, show):
        seat = Seat.objects.first()

        response = _post(views.select_seats, show.id, data={f"seat_{seat.id}": "normal"})
        assert response.status_code == 302
        assert response["Location"] == reverse(views.booking_overview, args=[show.id])
        reservation = Reservation.objects.get()
        assert reservation.tickets == {str(seat.id): "normal"}

    def test_select_seats__with_finalized_reservation_in_session__gives_new_reservation(self, show):
        reservation = _reservation(show, finalized=True)

        response = _get(views.select_seats, show.id, session={f"show_{show.id}": reservation.id})
        assert response._request.session[f"show_{show.id}"] != reservation.id


@pytest.mark.django_db
class TestTickets:
    def test_ticket_detail(self, show):
        reservation = _reservation(show)
        ticket = f.CreateTicket(show=show, seat_id=list(reservation.tickets.keys())[0])
        response = _get(views.ticket_detail, reservation.id, ticket.ticket_code)
        assert response.status_code == 200

    def test_ticket_pdf(self, show):
        reservation = _reservation(show)
        ticket = f.CreateTicket(show=show, seat_id=list(reservation.tickets.keys())[0])
        response = _get(views.ticket_pdf, reservation.id, ticket.ticket_code)
        assert response.status_code == 200
        assert response["Content-Type"] == "application/pdf"


def _reservation(show, **kwargs):
    seat = Seat.objects.first()
    tickets = {str(seat.id): "normal"}
    return f.CreateReservation(tickets=tickets, session_timeout=timezone.now(), show=show, **kwargs)


def _post(view, *args, data=None, session=None):
    request = RequestFactory().post(reverse(view, args=args), data=data)
    _add_session(request, session)
    return view(request, *args)


def _get(view, *args, session=None):
    request = RequestFactory().get(reverse(view, args=args))
    _add_session(request, session)
    return view(request, *args)


def _add_session(request, session=None):
    session = session or {}
    middleware = SessionMiddleware()
    middleware.process_request(request)
    request.session.save()
    for key in session:
        request.session[key] = session[key]
    return request
