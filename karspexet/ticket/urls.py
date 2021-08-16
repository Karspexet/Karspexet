from django.urls import path

from karspexet.ticket import views

urlpatterns = [
    path("", views.home, name="ticket_home"),
    path("reservation/<reservation_code>/", views.reservation_detail, name="reservation_detail"),
    path("reservation/<reservation_code>/send_reservation_email/", views.send_reservation_email, name="send_reservation_email"),
    path("reservation/<reservation_id>/apply_voucher", views.apply_voucher, name="apply_voucher"),
    path("reservation/<reservation_id>/process_payment", views.process_payment, name="process_payment"),
    path("show/<show_id>/booking_overview/", views.booking_overview, name="booking_overview"),
    path("show/<show_id>/select_seats/", views.select_seats, name="select_seats"),
    path("show/<show_id>/cancel/", views.cancel_reservation, name="cancel_reservation"),
    path("stripe-webhooks/", views.stripe_webhooks),
    path("ticket/<reservation_id>-<ticket_code>.pdf", views.ticket_pdf, name="ticket_pdf"),
    path("ticket/<reservation_id>-<ticket_code>/", views.ticket_detail, name="ticket_detail"),
]
