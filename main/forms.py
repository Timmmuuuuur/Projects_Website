from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
class NewUserForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

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