from django.contrib import admin
from django.shortcuts import reverse
from django.utils.html import format_html, format_html_join

from karspexet.ticket.models import Account, PricingModel, Reservation, Ticket, Voucher


def show_link(self, obj=None):
    if obj is None:
        return ""
    return format_html('<a href="{}">{}</a>', admin_change_url(obj.show), obj.show)


def admin_change_url(obj):
    return reverse("admin:%s_%s_change" % (obj._meta.app_label, obj._meta.model_name), args=(obj.pk,))


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    fields = (
        "show_link",
        "reservation_code",
        "finalized",
        ("ticket_price", "total"),
        "session_timeout",
        "related_tickets",
        "tickets",
    )
    list_display = ("reservation_code", "show", "finalized", "ticket_price", "total", "session_timeout", "tickets")
    list_filter = ("finalized", "show")
    readonly_fields = ("show_link", "reservation_code", "related_tickets")

    show_link = show_link

    def related_tickets(self, obj=None):
        if obj is None:
            return ""
        tickets = [(admin_change_url(t), f"{t.seat}: {t.account.name}") for t in obj.ticket_set().all()]
        return format_html_join("<br>", '<a href="{0}">{1}</a>', tickets)


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    fields = ("show_link", "ticket_code", ("ticket_type", "price"), "seat", "account")
    list_display = ("ticket_code", "show", "price", "ticket_type", "seat", "account")
    raw_id_fields = ("account", "seat")
    readonly_fields = ("show_link", "ticket_code")

    show_link = show_link


class VoucherAdmin(admin.ModelAdmin):
    list_display = ("amount", "code", "expiry_date", "created_by")
    list_filter = ("expiry_date", "created_by")


class PricingModelAdmin(admin.ModelAdmin):
    list_display = ("seating_group", "prices", "valid_from")


class AccountAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone")


admin.site.register(Voucher, VoucherAdmin)
admin.site.register(PricingModel, PricingModelAdmin)
admin.site.register(Account, AccountAdmin)
