from django import forms


class CustomerEmailForm(forms.Form):
    email = forms.EmailField(
        required=True,
        label="E-postadress",
        widget=forms.TextInput(attrs={"placeholder": "E-postadress"}),
    )


class ContactDetailsForm(forms.Form):
    email = forms.EmailField(required=True)
    name = forms.CharField(required=False)
    phone = forms.CharField(required=False)
    reference = forms.CharField(required=False)
