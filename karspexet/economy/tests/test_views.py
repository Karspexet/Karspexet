from django.test import TestCase
from django.urls import reverse

from factories import factories as f


class TestOverview(TestCase):
    def test_only_staff_can_access_overview_page(self):
        url = reverse("economy_overview")
        response = self.client.get(url)
        assert response.status_code == 302

        user = f.CreateStaffUser(username="amon")
        self.client.force_login(user)

        response = self.client.get(url)
        assert "Föreställningsöversikt" in response.content.decode("utf-8")


class TestShowDetail(TestCase):
    def test_only_staff_can_access_detail_page(self):
        venue = f.CreateVenue(num_seats=1)
        seat = venue.seatinggroup_set.first().seat_set.first()
        show = f.CreateShow(venue=venue)
        f.CreateTicket(show=show, seat=seat)

        url = reverse("economy_show_detail", kwargs={"show_id": show.id})
        response = self.client.get(url)
        assert response.status_code == 302

        staff = f.CreateStaffUser(username="cmon")
        self.client.force_login(staff)

        response = self.client.get(url)
        self.assertContains(response, "Föreställningsöversikt")


class TestVouchers(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.staff = f.CreateStaffUser(username="bmon")

    def test_vouchers_list(self):
        url = reverse("economy_vouchers")
        assert self.client.get(url).status_code == 302

        self.client.force_login(self.staff)

        response = self.client.post(url, data={"note": "Rabbatkod ABC123", "amount": 100})
        assert response.status_code == 302

        response = self.client.get(url)
        self.assertContains(response, "Rabbatkod ABC123")

    def test_discounts_list(self):
        url = reverse("economy_discounts")
        assert self.client.get(url).status_code == 302

        self.client.force_login(self.staff)

        venue = f.CreateVenue(num_seats=1)
        seat = venue.seatinggroup_set.first().seat_set.first()
        reservation = f.CreateReservation(show__venue=venue, tickets={str(seat.id): "normal"})
        f.CreateDiscount(reservation=reservation, voucher__code="Rabbat")

        response = self.client.get(url)
        self.assertContains(response, "Rabbat")
