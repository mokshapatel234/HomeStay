from django import forms
from django.forms import fields
from django.forms.widgets import FileInput
from string import Template
from django.utils.safestring import mark_safe
from django.forms import ImageField
from django.conf import settings
from .models import *


class LoginForm(forms.Form):
    email = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "email",
                "class": "form-control"
            }
        ))
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password",
                "class": "form-control"
            }
        ))
    

class Add_clientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['first_name', 'last_name', 'email', 'password', 'profile_image', 'contact_no']


# class Add_propertyForm(forms.ModelForm):
    
#     class Meta:
#         model = Properties
#         fields = ['name', 'images', 'videos', 'price', 'description', 'address', 'status']