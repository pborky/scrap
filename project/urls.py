from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

from django.contrib import admin
import demo_app.urls
import app.urls
from app.models import Engine

admin.autodiscover()

admin.site.register((Engine,))

from .views import login,logout

urlpatterns = patterns('',
    # Home Page -- Replace as you prefer
    url(r'^', include(app.urls), name='app'),

    url(r'^login$', login, name='login'),
    url(r'^logout$', logout, name='logout'),

    url(r'^admin/', include(admin.site.urls), name='admin'),
    #url(r'^demo/', include(demo_app.urls)),
)
