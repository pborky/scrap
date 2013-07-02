from django import forms
from django.contrib.auth.models import User
from bootstrap_toolkit.widgets import BootstrapDateInput, BootstrapTextInput, BootstrapUneditableInput, BootstrapPasswordInput
from .models import Engine,Search


class SearchForm(forms.Form):
    engine = forms.ModelChoiceField(
        label='',
        empty_label = 'Select engine',
        required=True,
        queryset =  Engine.objects.filter(active=True),
    )

    q =  forms.CharField(
        label='',
        max_length=100,
        required=True,
        widget=BootstrapTextInput(attrs={'placeholder': 'Query string'}),
    )


class SearchResultsForm(forms.Form):
    class Meta:
        model = Search