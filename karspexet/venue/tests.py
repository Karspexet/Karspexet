from django.test import TestCase

from karspexet.venue.models import Venue


class VenueTests(TestCase):
    def test_display_venue(self):
        venue = Venue.objects.create(name="Södra teatern")
        response = self.client.get("/venue/%s/" % venue.pk)

        self.assertContains(response, "Södra teatern")
