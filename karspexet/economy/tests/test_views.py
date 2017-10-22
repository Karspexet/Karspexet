# coding: utf-8
from django.contrib.auth.models import User
from django.http import HttpRequest
from django.test import TestCase, Client
from django.utils import timezone

from factories import factories as f

from karspexet.economy import views

class TestOverview(TestCase):
    def test_only_staff_can_access_overview_page(self):
        client = Client()
        response = client.get("/economy/")
        assert response.status_code == 302

        user = User.objects.create_user("ture", email="ture@example.com")
        user.set_password("test")
        user.is_staff = True
        user.save()

        assert client.login(username="ture", password="test")

        response = client.get("/economy/")
        assert "Föreställningsöversikt" in response.content.decode("utf-8")


class TestShowDetail(TestCase):
    def test_only_staff_can_access_detail_page(self):
        production = f.CreateProduction()
        venue = f.CreateVenue()
        seating_group = f.CreateSeatingGroup(venue=venue)
        seat = f.CreateSeat(group=seating_group)
        show = f.CreateShow(date=timezone.now(), production=production, venue=venue)

        client = Client()
        response = client.get(f"/economy/{show.id}")
        assert response.status_code == 302

        user = User.objects.create_user("ture", email="ture@example.com")
        user.set_password("test")
        user.is_staff = True
        user.save()

        assert client.login(username="ture", password="test")

        response = client.get(f"/economy/{show.id}")
        assert "Föreställningsöversikt" in response.content.decode("utf-8")
