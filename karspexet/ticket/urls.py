from django.conf.urls import url

from karspexet.ticket import views

urlpatterns = [
    url(r"^show/(?P<show_slug>[\w\-]+)/select_seats/?$", views.select_seats, name="select_seats"),
    url(r"^reservation/(?P<reservation_id>\d+)/process_payment$", views.process_payment, name="process_payment"),
    url(r"^reservation/(?P<reservation_id>\d+)/apply_voucher$", views.apply_voucher, name="apply_voucher"),
    url(r"^show/(?P<show_slug>[\w\-]+)/booking_overview/?$", views.booking_overview, name="booking_overview"),
    url(r"^reservation/(?P<reservation_code>[A-Z0-9]+)/?$", views.reservation_detail, name="reservation_detail"),
    url(r"^ticket/(?P<reservation_id>\d+)-(?P<ticket_code>[A-Z0-9]+)/?$", views.ticket_detail, name="ticket_detail"),
    url(r"^ticket/(?P<reservation_id>\d+)-(?P<ticket_code>[A-Z0-9]+).pdf$", views.ticket_pdf, name="ticket_pdf"),
    url(r"^reservation/(?P<reservation_code>[A-Z0-9]+)/send_reservation_email$", views.send_reservation_email, name="send_reservation_email"),
    url(r"^cancel/(?P<show_id>\d+)/?$", views.cancel_reservation, name="cancel_reservation"),
    url(r"^stripe-webhooks/$", views.stripe_webhooks),
    url(r"^$", views.home, name="ticket_home"),
]
