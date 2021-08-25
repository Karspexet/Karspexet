from django.contrib import admin

from karspexet.show.models import Production, Show


@admin.register(Production)
class ProductionAdmin(admin.ModelAdmin):
    list_display = ("name", "alt_name")


@admin.register(Show)
class ShowAdmin(admin.ModelAdmin):
    list_display = ("production", "slug", "date_string")
    list_filter = ("production",)
    exclude = ("slug",)
    ordering = ("-pk",)
