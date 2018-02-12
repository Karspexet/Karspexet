from django.contrib import admin

from karspexet.ticket.models import Account, Reservation, Ticket, Voucher, PricingModel


class ReservationAdmin(admin.ModelAdmin):
    list_display = ('show', 'total', 'finalized', 'reservation_code', 'tickets')
    list_filter = ('finalized', 'show')


class TicketAdmin(admin.ModelAdmin):
    list_display = ('price', 'ticket_type', 'show', 'seat', 'account', 'ticket_code')


class VoucherAdmin(admin.ModelAdmin):
    list_display = ('amount', 'code', 'expiry_date', 'created_by')
    list_filter = ('expiry_date', 'created_by')


class PricingModelAdmin(admin.ModelAdmin):
    list_display = ('seating_group', 'prices', 'valid_from')

class AccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone')

admin.site.register(Reservation, ReservationAdmin)
admin.site.register(Ticket, TicketAdmin)
admin.site.register(Voucher, VoucherAdmin)
admin.site.register(PricingModel, PricingModelAdmin)
admin.site.register(Account, AccountAdmin)
