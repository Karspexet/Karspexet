from django.urls import path

from karspexet.economy import views

urlpatterns = [
    path("", views.overview, name="economy_overview"),
    path("<int:show_id>/", views.show_detail, name="economy_show_detail"),
    path("create_voucher/", views.create_voucher, name="economy_create_voucher"),
    path("discounts/", views.discounts, name="economy_discounts"),
    path("vouchers/", views.vouchers, name="economy_vouchers"),
]
