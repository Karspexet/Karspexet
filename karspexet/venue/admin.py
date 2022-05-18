from django.contrib import admin
from django.contrib.admin.options import IncorrectLookupParameters
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.html import format_html
from django_object_actions import DjangoObjectActions

from karspexet.ticket.models import PricingModel
from karspexet.utils import admin_change_url
from karspexet.venue.models import Seat, SeatingGroup, Venue


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
        url = admin_change_url(obj)
        return format_html('<a href="{}">Edit: {}</a>', url, obj)


class PricingModelInline(admin.TabularInline):
    model = PricingModel
    extra = 0
    fields = ["admin_link"]
    readonly_fields = ["admin_link"]

    @classmethod
    def admin_link(cls, obj):
        if not obj.pk:
            return ""
        url = admin_change_url(obj)
        return format_html('<a href="{}">Edit: {}</a>', url, obj)


@admin.register(Venue)
class VenueAdmin(DjangoObjectActions, admin.ModelAdmin):
    inlines = [SeatingGroupInline]
    readonly_fields = ["num_seats"]

    change_actions = ["add_seats"]

    @admin.display(description="Lägg till platser")
    def add_seats(self, request, obj):
        return redirect("manage_seats", venue_id=obj.id)

    @admin.display(description="Number of seats")
    def num_seats(self, obj):
        if not obj:
            return ""
        return Seat.objects.filter(group__venue=obj).count()


@admin.register(SeatingGroup)
class SeatingGroupAdmin(admin.ModelAdmin):
    inlines = [PricingModelInline]
    raw_id_fields = ("venue",)
    readonly_fields = ["seat_admin_link"]

    @admin.display(description="Link to Seat-admin")
    def seat_admin_link(self, obj):
        if not obj:
            return ""
        link = reverse("admin:venue_seat_changelist") + f"?group_id={obj.id}"
        return format_html('<a href="{}">{}</a>', link, "Filtered Seat-admin")


@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ("name", "group")
    raw_id_fields = ("group",)
    list_filter = [VenueFilter]
