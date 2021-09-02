from django import forms


class CustomerEmailForm(forms.Form):
    email = forms.EmailField(
        required=True,
        label="E-postadress",
        widget=forms.TextInput(attrs={
            "placeholder": "E-postadress",
            "class": "p-2 w-full box-border",
        }),
    )
