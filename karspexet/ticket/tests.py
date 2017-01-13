from datetime import datetime

from django.shortcuts import reverse
from django.test import TestCase
from django.utils import timezone

from karspexet.show.models import Show, Production
from karspexet.ticket import views

from karspexet.venue.models import Venue, SeatingGroup


class TestHome(TestCase):
    def test_home(self):
        venue = Venue.objects.create(name="Teater 1")
        production = Production.objects.create(name="Uppsättningen")
        date = timezone.datetime(2017,1,30,18,0)
        show = Show.objects.create(date=date, production=production, venue=venue)

        response = self.client.get(reverse(views.home))

        self.assertContains(response, production.name)
        self.assertContains(response, show.date_string())


class TestSelect_seats(TestCase):
    def test_select_seats(self):
        venue = Venue.objects.create(name="Teater 1")
        seatinggroup = SeatingGroup.objects.create(name="prisgrupp 1", venue=venue)
        production = Production.objects.create(name="Uppsättningen")
        show = Show.objects.create(date=timezone.now(), production=production, venue=venue)

        response = self.client.get(reverse(views.select_seats, args=[show.id]))

        self.assertContains(response, "Köp biljetter för Uppsättningen")


