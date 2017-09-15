from django.test import TestCase
from django.utils import timezone

from karspexet.show.models import Show, Production
from karspexet.venue.models import Venue


class ShowTests(TestCase):
    def test_stuff(self):
        production = Production()
        production.save()

        venue = Venue()
        venue.save()

        show = Show(date=timezone.now(), production=production, venue=venue)
        show.save()
