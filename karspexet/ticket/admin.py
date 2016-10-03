from django.contrib import admin

from karspexet.ticket.models import Reservation, Ticket, Voucher


class ReservationAdmin(admin.ModelAdmin):
    pass


class TicketAdmin(admin.ModelAdmin):
    pass


class VoucherAdmin(admin.ModelAdmin):
    pass


admin.site.register(Reservation, ReservationAdmin)
admin.site.register(Ticket, TicketAdmin)
admin.site.register(Voucher, VoucherAdmin)
