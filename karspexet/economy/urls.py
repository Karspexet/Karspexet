from django.conf.urls import url

from karspexet.economy import views

urlpatterns = [
    url(r"^$", views.overview, name="economy_overview"),
    url(r"^(?P<show_id>\d+)$", views.show_detail, name="economy_show_detail"),
]
