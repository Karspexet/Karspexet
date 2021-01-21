from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView

urlpatterns = [
    url(r"^admin/", admin.site.urls),
    url(r"^economy/", include("karspexet.economy.urls")),
    url(r"^ticket/", include("karspexet.ticket.urls")),
    url(r"^500/", TemplateView.as_view(template_name="500.html")),
    url(r"^", include("cms.urls")),
]

urlpatterns = static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT, show_indexes=settings.DEBUG) + urlpatterns
