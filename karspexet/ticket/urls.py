from django.conf.urls import url

from karspexet.ticket import views

urlpatterns = [
    url(r"^show/(?P<show_id>\d+)/select_seats/?$", views.select_seats, name="select_seats"),
    url(r"^reservation/(?P<reservation_id>\d+)/process_payment$", views.process_payment, name="process_payment"),
    url(r"^booking_overview/?$", views.booking_overview, name="booking_overview"),
    url(r"^reservation/(?P<reservation_code>[A-Z0-9]+)/?$", views.reservation_detail, name="reservation_detail"),
    url(r"^ticket/(?P<reservation_code>[A-Z0-9]+)-(?P<ticket_id>\d+)/?$", views.ticket_detail, name="ticket_detail"),
    url(r"^$", views.home),
]
