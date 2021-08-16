from django.urls import path

from karspexet.venue import views

urlpatterns = [
    path("<venue_id>/seats/", views.manage_seats, name="manage_seats"),
]
