from django.contrib.auth.forms import UserCreationForm
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




class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']



class WorkDayForm(forms.Form):
    time_start = forms.TimeField(widget=forms.TextInput(attrs={'placeholder': 'HH:MM'}))
    time_end = forms.TimeField(widget=forms.TextInput(attrs={'placeholder': 'HH:MM'}))
    start_date = forms.DateField(widget=forms.DateInput(attrs={'class': 'datepicker'}))
    end_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'class': 'datepicker'}))



class HolidayForm(forms.Form):
    start_date_free = forms.DateField(widget=forms.DateInput(attrs={'class': 'datepicker'}))
    end_date_free = forms.DateField(required=False, widget=forms.DateInput(attrs={'class': 'datepicker'}))
    date_free=forms.BooleanField(widget=forms.HiddenInput(),initial=True)
    time_start = forms.TimeField(widget=forms.HiddenInput(),initial="00:00")
    time_end = forms.TimeField(widget=forms.HiddenInput(),initial="00:00")


def is_login_repeated(value):
    """
     not used just to practise
     """
    user = User.objects.filter(username=value)
    if user.count():
        raise forms.ValidationError("That user is already taken , please select another ")

class AddUserForm(forms.Form):
    """
    not used just to practise
    """
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
                "Repeated password is not the same"
            )
