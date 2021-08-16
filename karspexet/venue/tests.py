from django.shortcuts import reverse
from django.test import TestCase

from factories import factories as f
from karspexet.venue.models import Seat


class TestVenueViews(TestCase):
    def setUp(self):
        staff = f.CreateStaffUser()
        self.client.force_login(staff)

    def test_manage_seats(self):
        venue = f.CreateVenue()
        group = f.CreateSeatingGroup(venue=venue)

        url = reverse("manage_seats", args=[venue.id])
        response = self.client.get(url)
        assert response.status_code == 200

        response = self.client.post(url, data={"group": group.id, "num_seats": 2})
        assert response.status_code == 302
        assert Seat.objects.count() == 2
