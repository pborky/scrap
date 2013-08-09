from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

from .views import search, home, scrap, search_results, search_submit, site_ban, site_edit, site_content_detail, site_content_edit, site_edit_name, site_edit_category, search_results_all


urlpatterns = patterns('',
    home.url(),
    search.url(),
    search_results.url(),
    search_results_all.url() ,
    search_submit.url(),
    site_ban.url(),
    site_edit.url(),
    site_edit_name.url(),
    site_edit_category.url(),
    site_content_detail.url(),
    site_content_edit.url(),
    scrap.url(),
)
