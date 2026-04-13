from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe


def _auth_field_classes(widget_attrs):
    """Materialize skips styling when .browser-default is set — keeps inputs compact."""
    c = widget_attrs.get("class", "") or ""
    extra = "browser-default portfolio-form-input"
    widget_attrs["class"] = f"{c} {extra}".strip()


class PortfolioAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _auth_field_classes(self.fields["username"].widget.attrs)
        _auth_field_classes(self.fields["password"].widget.attrs)
        self.fields["username"].widget.attrs["autocomplete"] = "username"
        self.fields["password"].widget.attrs["autocomplete"] = "current-password"


class NewUserForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in ("username", "email", "password1", "password2"):
            _auth_field_classes(self.fields[name].widget.attrs)
        self.fields["username"].widget.attrs["autocomplete"] = "username"
        self.fields["email"].widget.attrs["autocomplete"] = "email"
        self.fields["password1"].widget.attrs["autocomplete"] = "new-password"
        self.fields["password2"].widget.attrs["autocomplete"] = "new-password"

    def save(self, commit=True):
        user = super(NewUserForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

class AddressInputForm(forms.Form):

    address_string = forms.CharField(label=mark_safe("Address values, as per the convention outlined above"))
    vehicle_count = forms.CharField(label = mark_safe("The number of vehicles in your target fleet"))

class UniAdminForm(forms.Form):

    gre = forms.CharField(label=mark_safe("GRE Score"))
    gpa = forms.CharField(label = mark_safe("GPA"))
    rank = forms.CharField(label=mark_safe("Rank of your institution"))