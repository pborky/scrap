from django.shortcuts import redirect

__author__ = 'pborky'

from .forms import SearchForm
from project.helpers import view
from django.views.decorators import http, cache

@view(
    r'^demo$',
    template = 'home.html',
)
@http.require_http_methods(('GET','POST'))
def demo(request, *args, **kwargs):
    if request.method == 'POST':
        pass
    elif request.method == 'GET':
        pass

@view(
    r'^demo2$',
    template = 'home.html',
)
class demo2:

    def post(self, request, *args, **kwargs):
        pass

    def get(self, request, *args, **kwargs):
        pass
@view(
    r'^demo3$',
    template = 'home.html',
)
class demo3:

    @staticmethod
    def post(request, *args, **kwargs):
        pass

    @staticmethod
    def get(request, *args, **kwargs):
        pass


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
    form_cls = (SearchForm,),
    invalid_form_msg = 'You must select engine and enter query string.',
)
class search:

    @staticmethod
    def get(request, *args, **kwargs):
        pass

    @staticmethod
    def post(request, *args, **kwargs):
        pass

@view(
    r'^scrap$',
    template = 'scrap.html',
)
class scrap:

    @staticmethod
    def get(request, *args, **kwargs):
        pass