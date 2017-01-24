from django.conf.urls import url

from karspexet.ticket import views

urlpatterns = [
    url(r"^show/(?P<show_id>\d+)/select_seats$", views.select_seats, name="select_seats"),
    url(r"^$", views.home),
]
