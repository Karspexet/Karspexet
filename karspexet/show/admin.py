from django.contrib import admin

from karspexet.show.models import Production, Show


class ProductionAdmin(admin.ModelAdmin):
    pass


class ShowAdmin(admin.ModelAdmin):
    pass


admin.site.register(Production, ProductionAdmin)
admin.site.register(Show, ShowAdmin)
