# coding: utf-8
from django.shortcuts import reverse
from django.test import TestCase, RequestFactory
from django.utils import timezone

from karspexet.show.models import Show, Production
from karspexet.ticket import views

from karspexet.venue.models import Venue, SeatingGroup

import pytest


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

        response = self.client.get(reverse(views.select_seats, args=[show.id]))

        self.assertContains(response, "Köp biljetter för Uppsättningen")
