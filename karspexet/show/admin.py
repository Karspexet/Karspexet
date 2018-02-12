from django.contrib import admin

from karspexet.show.models import Production, Show


class ProductionAdmin(admin.ModelAdmin):
    list_display = ('name', 'alt_name')


class ShowAdmin(admin.ModelAdmin):
    list_display = ('production', 'slug', 'date_string')


admin.site.register(Production, ProductionAdmin)
admin.site.register(Show, ShowAdmin)
