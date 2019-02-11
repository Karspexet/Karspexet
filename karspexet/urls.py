from django.conf.urls import url, include
from django.contrib import admin

urlpatterns = [
    url(r"^admin/", admin.site.urls),
    url(r"^economy/", include("karspexet.economy.urls")),
    url(r"^ticket/", include("karspexet.ticket.urls")),
    url(r"^", include("cms.urls")),
]
