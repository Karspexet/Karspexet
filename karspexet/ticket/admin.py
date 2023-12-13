from django.contrib import admin
from django.utils.html import format_html, format_html_join

from karspexet.ticket.models import (
    Account,
    Discount,
    PricingModel,
    Reservation,
    Ticket,
    Voucher,
)
from karspexet.utils import admin_change_url


def admin_change_link(obj) -> str:
    if obj is None:
        return ""
    return format_html('<a href="{}">{}</a>', admin_change_url(obj), obj)


def show_link(self, obj=None):
    return admin_change_link(obj.show if obj else None)


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    fields = (
        "show_link",
        "related_tickets",
        "reservation_code",
        "finalized",
        ("ticket_price", "total"),
        "session_timeout",
        "tickets",
    )
    search_fields = ("reservation_code",)
    list_select_related = ["show", "show__production"]
    list_display = (
        "reservation_code",
        "show",
        "finalized",
        "ticket_price",
        "total",
        "session_timeout",
        "tickets",
    )
    list_filter = ("finalized", "show")
    readonly_fields = ("show_link", "reservation_code", "related_tickets")

    show_link = show_link

    def has_add_permission(self, obj):
        return False

    def lookup_allowed(self, key, value):
        return True

    def related_tickets(self, obj=None):
        if obj is None:
            return ""
        tickets = [
            (admin_change_url(t), f"{t.seat}: {t.account.name}")
            for t in obj.ticket_set().all()
        ]
        return format_html_join("<br>", '<a href="{0}">{1}</a>', tickets)


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    fields = (
        "show_link",
        "reservation",
        "ticket_code",
        ("ticket_type", "price"),
        "seat",
        "account",
    )
    search_fields = ("reservation__reservation_code", "ticket_code")
    list_display = ("ticket_code", "show", "price", "ticket_type", "seat", "account")
    raw_id_fields = ("account", "seat")
    readonly_fields = ("show_link", "reservation", "ticket_code")

    show_link = show_link

    def has_add_permission(self, obj):
        return False

    def lookup_allowed(self, key, value):
        return True

    def reservation(self, obj=None):
        return admin_change_link(obj.get_reservation() if obj else None)


class IsUsedFilter(admin.SimpleListFilter):
    title = "used"
    parameter_name = "used"

    def lookups(self, request, model_admin):
        return (("used", "Used"), ("unused", "Unused"))

    def queryset(self, request, queryset):
        if self.value() == "used":
            return queryset.filter(discount__isnull=False)
        elif self.value() == "unused":
            return queryset.filter(discount__isnull=True)
        return queryset


@admin.register(Voucher)
class VoucherAdmin(admin.ModelAdmin):
    list_display = ("code", "amount", "note", "is_used")
    list_filter = (IsUsedFilter, "expiry_date")
    list_select_related = ("discount",)
    fields = (
        ("is_used", "used_by"),
        ("note", "amount"),
        "code",
        "expiry_date",
        "created_by",
    )
    readonly_fields = ("used_by", "is_used")

    def lookup_allowed(self, key, value):
        return True

    def get_changeform_initial_data(self, request):
        return {"created_by": request.user}

    @admin.display(boolean=True)
    def is_used(self, obj):
        if not obj:
            return False
        try:
            return bool(obj.discount)
        except Discount.DoesNotExist:
            return False

    def used_by(self, obj):
        if not obj:
            return ""
        if not obj.discount:
            return ""
        return admin_change_link(obj.discount.reservation)


@admin.register(PricingModel)
class PricingModelAdmin(admin.ModelAdmin):
    list_display = ("_venue", "_from", "prices")
    list_select_related = ["seating_group", "seating_group__venue"]

    @admin.display(description="Venue / Group")
    def _venue(self, obj):
        return f"{obj.seating_group.venue} / {obj.seating_group}"

    @admin.display(description="Valid from")
    def _from(self, obj):
        return f"{obj.valid_from:%Y-%m-%d %H:%M}"


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone")
