from django.contrib import admin

from karspexet.ticket.models import Account, Reservation, Ticket, Voucher, PricingModel


class ReservationAdmin(admin.ModelAdmin):
    pass


class TicketAdmin(admin.ModelAdmin):
    pass


class VoucherAdmin(admin.ModelAdmin):
    pass


class PricingModelAdmin(admin.ModelAdmin):
    pass

class AccountAdmin(admin.ModelAdmin):
    pass

admin.site.register(Reservation, ReservationAdmin)
admin.site.register(Ticket, TicketAdmin)
admin.site.register(Voucher, VoucherAdmin)
admin.site.register(PricingModel, PricingModelAdmin)
admin.site.register(Account, AccountAdmin)
