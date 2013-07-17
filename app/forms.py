from django.forms import HiddenInput, SelectMultiple
from bootstrap_toolkit.widgets import BootstrapDateInput, BootstrapTextInput
from django.utils.html import format_html
from project.widgets import ModelForm,Uneditable
from .models import Search, SIteContent, Whois, Ip

class SearchForm(ModelForm):
    class Meta:
        model = Search
        fields = ('engine', 'q',)
        attrs = {
            'engine': {
                'label': '',
                'empty_label': 'Select engine',
                'queryset': model.engine.get_query_set().filter(active=True),
                },
            'q': {
                'label': '',
                'widget': BootstrapTextInput(attrs={'placeholder': 'Query string'}),
                },
            }

class SiteContentForm(ModelForm):
    class Meta:
        model = SIteContent
        fields = ('site', 'last_update', 'shipment', 'type', 'links')
        attrs = {
            'site': {
                'widget': HiddenInput(),
            },
            'last_update': {
                'label': 'Last updated',
                'widget': BootstrapDateInput(attrs={'class': 'datepicker', 'data-provide':'datepicker-inline' }),
            },
            'shipment': {
                'label': 'Shipment method',
                'help_text': '',
            },
            'type': {
                'label': 'Shop type',
                'empty_label': 'Select shop type'
            },
            'links': {
                'label': 'Links to other sites',
                'help_text': '',
                },
            }


class SiteContentReadOnlyForm(ModelForm):
    class Meta:
        model = SIteContent
        fields = ('site', 'last_update', 'shipment', 'type', 'links')
        attrs = {
            'site': {
                'widget': HiddenInput(attrs={'disabled':True}),
                },
            'last_update': {
                'label': 'Last updated',
                'widget': BootstrapDateInput(attrs={'disabled':True}),
                },
            'shipment': {
                'label': 'Shipment method',
                'help_text': '',
                'widget': Uneditable(
                        value_calback=lambda qs,selected: ', '.join( shp.name for shp in qs if shp.id in selected )
                    ),
                },
            'type': {
                'label': 'Shop type',
                'widget': Uneditable(
                        value_calback=lambda qs,selected: ', '.join( type.name for type in qs if type.id in selected )
                    ),
            },
            'links': {
                'label': 'Links to other sites',
                'help_text': '',
                'widget': Uneditable(
                        value_calback=lambda qs,selected: [format_html(u'<a href="{0}">{1}</a>', lnk.url, lnk.name) for lnk in qs if lnk.id in selected ] ,
                    ),
                },
            }


class WhoisReadOnlyForm(ModelForm):
    class Meta:
        model = Whois
        fields = ('date_from', 'contact', 'address1', 'address2')
        attrs = {
            'date_from': {
                'label': 'Whois registration date',
                'widget': BootstrapDateInput(attrs={'disabled':True}),
                },
            'contact': {
                'label': 'Whois contact',
                'widget': Uneditable(value_calback=lambda qs,selected: ', '.join(filter(None, selected))),
                },
            'address1': {
                'label': 'Whois address (city)',
                'widget': Uneditable(value_calback=lambda qs,selected: ', '.join(filter(None, selected))),
                },
            'address2': {
                'label': 'Whois address (country code)',
                'widget': Uneditable(value_calback=lambda qs,selected: ', '.join(filter(None, selected))),
                },
            }

class IpReadOnlyForm(ModelForm):
    class Meta:
        model = Ip
        fields = ('address', 'country' )
        attrs = {
            'address': {
                'label': 'IP address',
                'widget': Uneditable(),
                },
            'country': {
                'label': 'IP country code',
                'widget': Uneditable( ),
                },
            }