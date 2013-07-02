from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

from .views import search, home, scrap, search_results, search_submit


urlpatterns = patterns('',
    home.url(),
    search.url(),
    search_results.url(),
    search_submit.url(),
    scrap.url(),
)
