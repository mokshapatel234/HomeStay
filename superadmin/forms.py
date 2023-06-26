from django import forms
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


class AdminTermsAndpolicyForm(forms.ModelForm):
    class Meta:
        model = TermsandPolicy
        fields = ['user','terms_and_condition', 'privacy_policy']
        widgets = {
            'terms_and_condition': forms.Textarea(attrs={'class': 'ckeditor'}),
            'privacy_policy': forms.Textarea(attrs={'class': 'ckeditor'}),
        }

class PropertyTermsForm(forms.ModelForm):
    class Meta:
        model = PropertyTerms
        fields = ['terms']
        widgets = {
            'terms': forms.Textarea(attrs={'class': 'ckeditor'}),
        }