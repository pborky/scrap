from django.forms import Form, ModelForm, ModelChoiceField, CharField, DateField, ModelMultipleChoiceField, TextInput, HiddenInput
from django.contrib.auth.models import User
from bootstrap_toolkit.widgets import BootstrapDateInput, BootstrapTextInput, BootstrapUneditableInput, BootstrapPasswordInput
from .models import Engine,Search, SearchResult, SIteContent, Site, ShipmentMethod, SiteType


class SearchForm(Form):
    engine = ModelChoiceField(
        label='',
        empty_label = 'Select engine',
        required=True,
        queryset =  Engine.objects.filter(active=True),
    )

    q =  CharField(
        label='',
        max_length=100,
        required=True,
        widget=BootstrapTextInput(attrs={'placeholder': 'Query string'}),
    )


class SearchForm2(ModelForm):
    class Meta:
        model = Search
        exclude = ('date',)

class SiteContentForm(ModelForm):
    class Meta:
        model = SIteContent
        fields = ('site', 'last_update', 'shipment', 'type', 'links')
        labels = {
            'last_update': 'Last updated',
            'shipment': 'Shipment method',
            'type': 'Shop type',
            'links': 'Links to other sites',
            }
        help_texts = {
            'last_update': 'Some useful help text.',
            'shipment': 'Shipment method',
            'type': 'Shop type',
            'links': 'Links to other sites',
            }
        widgets = {
            'site': HiddenInput(),
            'last_update': BootstrapDateInput(attrs={'class': 'datepicker'}),
            }
        error_messages = {
        }
