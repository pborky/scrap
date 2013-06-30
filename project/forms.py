__author__ = 'pborky'

from django import forms
from django.contrib.auth.models import User
from bootstrap_toolkit.widgets import BootstrapDateInput, BootstrapTextInput, BootstrapUneditableInput, BootstrapPasswordInput

class LoginForm(forms.Form):
    def __init__(self,*args,**kwargs):
        kwargs['auto_id'] = False
        super(LoginForm,self).__init__(*args,**kwargs)

    username = forms.CharField (
        max_length=100,
        required=True,
        widget=BootstrapTextInput(attrs={'placeholder': 'Username'}),
    )
    password = forms.CharField (
        max_length=100,
        required=True,
        widget=BootstrapPasswordInput(attrs={'placeholder': 'Password'}),
    )

    def clean(self):
        return super(LoginForm, self).clean()