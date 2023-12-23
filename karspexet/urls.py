from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView

urlpatterns = [
    path("500/", TemplateView.as_view(template_name="500.html")),
    path("admin/", admin.site.urls),
    path("economy/", include("karspexet.economy.urls")),
    path("venue/", include("karspexet.venue.urls")),
    path("ticket/", include("karspexet.ticket.urls")),
    re_path(r"^favicon\.ico$", RedirectView.as_view(url="/static/favicon.ico", permanent=True)),
    # Important to keep this last
    path("", include("cms.urls")),
]

urlpatterns = static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT, show_indexes=settings.DEBUG) + urlpatterns
urlpatterns = static(settings.MEDIA_THUMBS_URL, document_root=settings.MEDIA_THUMBS_ROOT, show_indexes=settings.DEBUG) + urlpatterns
urlpatterns = static(settings.MEDIA_FILER_URL, document_root=settings.MEDIA_FILER_ROOT, show_indexes=settings.DEBUG) + urlpatterns
