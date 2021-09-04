from django import forms


class CustomerEmailForm(forms.Form):
    email = forms.EmailField(
        required=True,
        label="E-postadress",
        widget=forms.TextInput(attrs={"placeholder": "E-postadress"}),
    )


class ContactDetailsForm(forms.Form):
    name = forms.CharField(required=True)
    phone = forms.CharField(required=False)
    email = forms.EmailField(required=True)
    reference = forms.CharField(required=False)
