from django.contrib import admin
from django.shortcuts import reverse
from django.utils.html import format_html

from karspexet.venue.models import Seat, SeatingGroup, Venue


def _admin_change_link(obj):
    return reverse('admin:%s_%s_change' % (obj._meta.app_label, obj._meta.model_name), args=[obj.id])


class SeatingGroupInline(admin.StackedInline):
    model = SeatingGroup
    extra = 1
    readonly_fields = ['admin_link']

    @classmethod
    def admin_link(cls, obj):
        url = _admin_change_link(obj)
        return format_html(u'<a href="{}">Edit: {}</a>', url, obj)


class SeatInline(admin.StackedInline):
    model = Seat
    extra = 1


class VenueAdmin(admin.ModelAdmin):
    inlines = [SeatingGroupInline]


class SeatingGroupAdmin(admin.ModelAdmin):
    inlines = [SeatInline]


class SeatAdmin(admin.ModelAdmin):
    pass

admin.site.register(Venue, VenueAdmin)
admin.site.register(Seat, SeatAdmin)
admin.site.register(SeatingGroup, SeatingGroupAdmin)
