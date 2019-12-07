# coding: utf-8
from unittest import mock

import pytest
from django.contrib.sessions.middleware import SessionMiddleware
from django.shortcuts import reverse
from django.test import RequestFactory, TestCase
from django.utils import timezone

from factories import factories as f
from factories.fixtures import show, user
from karspexet.show.models import Production, Show
from karspexet.ticket import views
from karspexet.ticket.models import Discount, Reservation, Seat, Voucher
from karspexet.venue.models import SeatingGroup, Venue


class TestHome(TestCase):
    def setUp(self):
        rf = RequestFactory()
        self.request = rf.get(reverse(views.home))
        self.tomorrow = timezone.now() + timezone.timedelta(days=1)

    def test_home_lists_visible_upcoming_shows(self):
        venue = Venue.objects.create(name="Teater 1")
        production = Production.objects.create(name="Uppsättningen")
        yesterday = timezone.now() - timezone.timedelta(days=1)
        show = Show.objects.create(date=self.tomorrow, production=production, venue=venue)
        invisible_show = Show.objects.create(date=self.tomorrow, production=production, venue=venue, visible=False)
        old_show = Show.objects.create(date=yesterday, production=production, venue=venue)

        response = views.home(self.request)

        shows = response.context_data["upcoming_shows"]

        assert show in shows
        assert old_show not in shows

    def test_home_contains_only_visible_shows(self):
        venue = Venue.objects.create(name="Teater 1")
        production = Production.objects.create(name="Uppsättningen")
        show = Show.objects.create(date=self.tomorrow, production=production, venue=venue)
        invisible_show = Show.objects.create(date=self.tomorrow, production=production, venue=venue, visible=False)

        response = views.home(self.request)

        shows = response.context_data["upcoming_shows"]

        assert show in shows
        assert invisible_show not in shows


class TestSelect_seats(TestCase):
    def test_select_seats(self):
        venue = Venue.objects.create(name="Teater 1")
        seatinggroup = SeatingGroup.objects.create(name="prisgrupp 1", venue=venue)
        production = Production.objects.create(name="Uppsättningen")
        show = Show.objects.create(date=timezone.now(), production=production, venue=venue)

        response = self.client.get(reverse(views.select_seats, args=[show.slug]))

        self.assertContains(response, "Köp biljetter för Uppsättningen")


class TestOverview(TestCase):
    @mock.patch("karspexet.ticket.views.payment", autospec=True)
    def test_booking_overview_with_active_session(self, mock_payment):
        venue = f.CreateVenue()
        group = f.CreateSeatingGroup(venue=venue)
        f.CreatePricingModel(seating_group=group, prices={'student': 200, 'normal': 250}, valid_from=timezone.now())
        seat = f.CreateSeat(group=group)
        production = f.CreateProduction()
        show = f.CreateShow(production=production, venue=venue, date=timezone.now())
        reservation = f.CreateReservation(
            tickets={str(seat.id): "normal"},
            session_timeout=timezone.now(),
            show=show,
        )
        session = self.client.session
        session['show_%s' % show.id] = str(reservation.id)
        session.save()
        mock_payment_intent = object()
        mock_payment.get_payment_intent_from_reservation.return_value = mock_payment_intent

        url = reverse(views.booking_overview, args=[show.slug])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["reservation"], reservation)
        self.assertEqual(response.context["stripe_payment_indent"], mock_payment_intent)


class TestWebhooks(TestCase):
    def test_stripe_webhooks(self):
        payload = {"type": "unknown"}
        url = reverse(views.stripe_webhooks)
        response = self.client.post(url, data=payload, content_type="application/json")
        assert response.status_code == 400

        payload = {"type": "payment_intent.succeeded"}
        response = self.client.post(url, data=payload, content_type="application/json")
        assert response.status_code == 400


@pytest.mark.django_db
def test_cancelling_a_discounted_reservation_allows_voucher_for_reuse(show, user):
    seat = Seat.objects.first()
    tickets = {str(seat.id): 'normal'}
    reservation = f.CreateReservation(tickets=tickets, session_timeout=timezone.now(), show=show)
    voucher = Voucher.objects.create(amount=100, created_by=user)
    discount = reservation.apply_voucher(voucher.code)

    rf = RequestFactory()
    request = rf.get(reverse(views.cancel_reservation, args=[show.id]))
    middleware = SessionMiddleware()
    middleware.process_request(request)
    request.session.save()
    request.session[f"show_{show.id}"] = reservation.id

    response = views.cancel_reservation(request, show_id=show.id)

    assert Reservation.objects.filter(pk=reservation.id).count() == 0
    assert Discount.objects.filter(pk=discount.id).count() == 0


@pytest.mark.django_db
def test_select_seats__with_finalized_reservation_in_session__gives_new_reservation(show):
    seat = Seat.objects.first()
    tickets = {str(seat.id): 'normal'}
    reservation = f.CreateReservation(
        finalized=True,
        tickets=tickets,
        session_timeout=timezone.now(),
        show=show
    )

    rf = RequestFactory()
    request = rf.get(reverse(views.cancel_reservation, args=[show.id]))
    middleware = SessionMiddleware()
    middleware.process_request(request)
    request.session.save()
    request.session[f"show_{show.id}"] = reservation.id

    response = views.select_seats(request, show_slug=show.slug)
    assert response._request.session[f"show_{show.id}"] != reservation.id
