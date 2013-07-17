from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

from .views import search, home, scrap, search_results, search_submit, site_ban, site_edit, site_content_detail, site_content_edit


urlpatterns = patterns('',
    home.url(),
    search.url(),
    search_results.url(),
    search_submit.url(),
    site_ban.url(),
    site_edit.url(),
    site_content_detail.url(),
    site_content_edit.url(),
    scrap.url(),
)
