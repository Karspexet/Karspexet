from django.test import Client, TestCase
from django.utils import timezone

from factories import factories as f


class TestOverview(TestCase):
    def setUp(self):
        self.client = Client()

    def test_only_staff_can_access_overview_page(self):
        response = self.client.get("/economy/")
        assert response.status_code == 302

        f.CreateStaffUser(username="ture", password="test")
        assert self.client.login(username="ture", password="test")

        response = self.client.get("/economy/")
        assert "Föreställningsöversikt" in response.content.decode("utf-8")


class TestShowDetail(TestCase):
    def setUp(self):
        self.client = Client()

    def test_only_staff_can_access_detail_page(self):
        production = f.CreateProduction()
        venue = f.CreateVenue()
        seating_group = f.CreateSeatingGroup(venue=venue)
        seat = f.CreateSeat(group=seating_group)
        show = f.CreateShow(date=timezone.now(), production=production, venue=venue)
        staff = f.CreateStaffUser(username="ture", password="test")

        response = self.client.get(f"/economy/{show.id}/")
        assert response.status_code == 302

        self.client.force_login(staff)

        response = self.client.get(f"/economy/{show.id}/")
        self.assertContains(response, "Föreställningsöversikt")
