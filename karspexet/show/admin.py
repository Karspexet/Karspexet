from django import forms
from django.contrib import admin
from django.utils import timezone

from karspexet.show.models import Production, Show


@admin.register(Production)
class ProductionAdmin(admin.ModelAdmin):
    list_display = ("name", "alt_name")


class ShowForm(forms.ModelForm):
    class Meta:
        model = Show
        fields = [
            "production",
            "venue",
            "date",
            "free_seating",
            "visible",
            "short_description",
        ]

    visible = forms.BooleanField(initial=False, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["production"].initial = Production.objects.last()


@admin.register(Show)
class ShowAdmin(admin.ModelAdmin):
    list_display = ("date_string", "production", "venue", "visible", "is_upcoming")
    list_select_related = ("production", "venue")
    list_filter = ("visible", "production")
    exclude = ("slug",)
    ordering = ("-pk",)
    form = ShowForm

    @admin.display(boolean=True)
    def is_upcoming(self, obj):
        return obj.date > timezone.now()
