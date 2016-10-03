from django.conf.urls import url

from karspexet.venue import views

urlpatterns = [
    url(r"^(?P<venue_id>\d+)/$", views.venue)
]
