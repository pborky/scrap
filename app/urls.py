from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

from .views import search, home, scrap, demo, demo2, demo3


urlpatterns = patterns('',
    home.url(),
    search.url(),
    scrap.url(),
    demo.url(),
    demo2.url(),
    demo3.url(),

    #url(r'^$', scrap, name='home'),
    #url(r'^search$', search, name='search'),
    #url(r'^scrap$', home, name='scrap'),
)
