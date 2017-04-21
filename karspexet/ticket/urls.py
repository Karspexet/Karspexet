from django.conf.urls import url

from karspexet.ticket import views

urlpatterns = [
    url(r"^show/(?P<show_id>\d+)/select_seats$", views.select_seats, name="select_seats"),
    url(r"^show/(?P<show_id>\d+)/payment$", views.payment, name="payment"),
    url(r"^reservation/(?P<reservation_id>\d+)/process_payment$", views.process_payment, name="process_payment"),
    url(r"^$", views.home),
]
