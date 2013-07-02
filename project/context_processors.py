from forms import LoginForm

__author__ = 'pborky'

from models import SiteData

def site_data(request):
    return {
        'site_data': dict((s.name, s.value) for s in SiteData.objects.all()),
        }

def login_form(request):
    return {
        'login_form': LoginForm()
    }