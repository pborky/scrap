from django import forms
from django.contrib.auth.models import User
from bootstrap_toolkit.widgets import BootstrapDateInput, BootstrapTextInput, BootstrapUneditableInput, BootstrapPasswordInput
from .models import Engine

class SearchForm(forms.Form):
    def __init__(self,*args,**kwargs):
        kwargs['auto_id'] = False
        super(SearchForm,self).__init__(*args,**kwargs)

    engine = forms.ModelChoiceField(
        empty_label = 'Select engine',
        required=True,
        queryset =  Engine.objects.filter(active=True),
    )

    q =  forms.CharField(
        max_length=100,
        required=True,
        widget=BootstrapTextInput(attrs={'placeholder': 'Query string'}),
    )

    def clean(self):
        return super(SearchForm, self).clean()

