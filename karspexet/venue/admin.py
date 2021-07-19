from django.contrib import admin
from django.contrib.admin.options import IncorrectLookupParameters
from django.shortcuts import reverse
from django.utils.html import format_html

from karspexet.venue.models import Seat, SeatingGroup, Venue


def _admin_change_link(obj):
    return reverse("admin:%s_%s_change" % (obj._meta.app_label, obj._meta.model_name), args=[obj.id])


class VenueFilter(admin.SimpleListFilter):
    title = "Teater"
    parameter_name = "venue"

    def lookups(self, request, model_admin):
        return [(venue.id, venue.name) for venue in Venue.objects.all()]

    def queryset(self, request, queryset):
        if self.value():
            try:
                queryset = queryset.filter(group__venue_id=self.value())
            except ValueError as e:
                raise IncorrectLookupParameters(e)
        return queryset


class SeatingGroupInline(admin.TabularInline):
    model = SeatingGroup
    extra = 0
    readonly_fields = ["admin_link"]

    @classmethod
    def admin_link(cls, obj):
        if not obj.pk:
            return ""
        url = _admin_change_link(obj)
        return format_html('<a href="{}">Edit: {}</a>', url, obj)


class SeatInline(admin.TabularInline):
    model = Seat
    extra = 0


@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    inlines = [SeatingGroupInline]


@admin.register(SeatingGroup)
class SeatingGroupAdmin(admin.ModelAdmin):
    inlines = [SeatInline]
    raw_id_fields = ("venue",)


@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ("name", "group")
    raw_id_fields = ("group",)
    list_filter = [VenueFilter]
