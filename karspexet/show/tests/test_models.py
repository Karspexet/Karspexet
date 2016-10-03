from django.test import TestCase

from datetime import datetime


from karspexet.show.models import Show, Production
from karspexet.venue.models import Venue


class ShowTests(TestCase):
    def test_stuff(self):
        production = Production()
        production.save()

        venue = Venue()
        venue.save()

        show = Show(date=datetime.today(), production=production, venue=venue)
        show.save()
