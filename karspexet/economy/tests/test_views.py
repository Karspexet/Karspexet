# coding: utf-8
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.http import HttpRequest

from karspexet.economy import views

class TestOverview(TestCase):
    def test_only_staff_can_access_page(self):
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
