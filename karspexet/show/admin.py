from django.contrib import admin
from django.utils import timezone

from karspexet.show.models import Production, Show


@admin.register(Production)
class ProductionAdmin(admin.ModelAdmin):
    list_display = ("name", "alt_name")


@admin.register(Show)
class ShowAdmin(admin.ModelAdmin):
    list_display = ("date_string", "production", "venue", "visible", "is_upcoming")
    list_select_related = ("production", "venue")
    list_filter = ("visible", "production")
    exclude = ("slug",)
    ordering = ("-pk",)

    @admin.display(boolean=True)
    def is_upcoming(self, obj):
        return obj.date > timezone.now()
