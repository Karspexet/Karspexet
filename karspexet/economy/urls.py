from django.conf.urls import url

from karspexet.economy import views

urlpatterns = [
    url(r"^$", views.overview)
]
