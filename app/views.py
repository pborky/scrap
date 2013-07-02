from django.contrib import messages
from django.shortcuts import redirect

__author__ = 'pborky'

from .forms import SearchForm
from project.helpers import view
from django.views.decorators import http, cache
from .models import SearchResult, SiteCategory, Search

@view(
    r'^$',
    template = 'home.html',
)
class home:

    @staticmethod
    def get(request, *args, **kwargs):
        pass

@view(
    r'^search$',
    template = 'search.html',
    form_cls = {'search':SearchForm,},
    invalid_form_msg = 'You must select engine and enter query string.',
)
class search:
    @staticmethod
    def get(request, forms):
        pass
    @staticmethod
    def post(request, forms):
        data = forms['search'].data
        if not (data['q'] == 'magicke houby' and data['engine'] == '1'):
            messages.warning(request, 'Default input has been set for demo purposes.')
        return redirect('search_results', searchid='1')

@view(
    r'^search2$',
    redirect_to='search_results',
    form_cls = {'search':SearchForm,},
    invalid_form_msg = 'You must select engine and enter query string.',
)
class search_submit:
    @staticmethod
    def post(request, forms):
        data = forms['search'].data
        if not (data['q'] == 'magicke houby' and data['engine'] == '1'):
            forms['search'] = SearchForm({'q': 'magicke houby', 'engine': '1'})
            messages.warning(request, 'Default input has been set for demo purposes.')
        return { 'searchid': '1' }


@view(
    r'^search/(?P<searchid>\d*)$',
    template = 'search.html',
    form_cls = {'search':SearchForm,},
    invalid_form_msg = 'You must select engine and enter query string.',
)
class search_results:
    @staticmethod
    def get(request, searchid, forms):
        search, = Search.objects.filter(id=int(searchid))
        forms['search'] = SearchForm({'q': search.q, 'engine': search.engine.id })
        return {
            'forms': forms,
            'results': SearchResult.objects.filter(search=search).order_by('sequence'),
            'categories': SiteCategory.objects.filter(active=True).order_by("id"),
            }

@view(
    r'^scrap$',
    template = 'scrap.html',
)
class scrap:

    @staticmethod
    def get(request, *args, **kwargs):
        pass