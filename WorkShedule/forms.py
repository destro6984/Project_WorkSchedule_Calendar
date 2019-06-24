from django.contrib.auth.models import User
from django.forms import forms
from .models import *
from django import forms
from django.forms import ModelForm
from django.forms.widgets import SelectDateWidget
from bootstrap_datepicker_plus import DatePickerInput
from functools import partial

class LoginUserForm(forms.Form):
    login = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


def is_login_repeated(value):
    user = User.objects.filter(username=value)
    if user.count():
        raise forms.ValidationError("That user is already taken , please select another ")


class AddUserForm(forms.Form):
    username = forms.CharField(validators=[is_login_repeated])
    password = forms.CharField(widget=forms.PasswordInput)
    repeat_password = forms.CharField(widget=forms.PasswordInput)
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField()

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        repeat_password = cleaned_data.get("repeat_password")
        if password != repeat_password:
            raise forms.ValidationError(
                "Powtórzone hasło nie jest takie samo"
            )


class WorkDayForm(forms.Form):
    date_day=forms.DateField(widget=forms.DateInput(attrs={'class': 'datepicker'}))
    time_start = forms.TimeField(widget=forms.TextInput(attrs={'placeholder': 'HH:MM'}))
    time_end = forms.TimeField(widget=forms.TextInput(attrs={'placeholder': 'HH:MM'}))

    # DateInput = partial(forms.DateInput, {'class': 'datetime-input'})
    # start_date = forms.DateField(widget=DateInput())
    # end_date = forms.DateField(widget=DateInput())

