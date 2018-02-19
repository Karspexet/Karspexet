from django.conf.urls import url

from karspexet.economy import views

urlpatterns = [
    url(r"^$", views.overview, name="economy_overview"),
    url(r"^(?P<show_id>\d+)$", views.show_detail, name="economy_show_detail"),
    url(r"^vouchers$", views.vouchers, name="economy_vouchers"),
    url(r"^create_voucher$", views.create_voucher, name="economy_create_voucher"),
    url(r"^discounts$", views.discounts, name="economy_discounts"),
]
