from django import forms


class CustomerEmailForm(forms.Form):
    email = forms.EmailField(
        required=True,
        label="E-postadress",
        widget=forms.TextInput(attrs={"placeholder": "E-postadress"}),
    )


class ContactDetailsForm(forms.Form):
    email = forms.EmailField(
        required=True,
        widget=forms.TextInput(
            attrs={"autocomplete": "email", "placeholder": "frank@example.com"}
        ),
    )
    name = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"autocomplete": "name", "placeholder": "Frank Hamer"}
        ),
    )
    phone = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"autocomplete": "tel", "placeholder": "070-1740605", "type": "rel"}
        ),
    )
    reference = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "field"}),
    )
