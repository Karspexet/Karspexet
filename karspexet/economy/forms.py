from django import forms

from karspexet.ticket.models import Voucher


class VoucherForm(forms.ModelForm):
    amount = forms.IntegerField(
        required=True,
        label="Belopp",
        min_value=1,
    )
    note = forms.CharField(
        required=True,
        label="Beskrivning",
        max_length=255,
        help_text="Tex. vem som ska få rabatten",
    )

    def __init__(self, created_by, **kwargs):
        super().__init__(**kwargs)
        self.instance.created_by = created_by

    class Meta:
        model = Voucher
        fields = ["amount", "note"]
