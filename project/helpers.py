import types

__author__ = 'pborky'


from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.decorators import http, cache
from django.http import HttpResponse
from django.conf.urls import patterns, include, url

from functional import combinator,partial,flip


class Decorator(object):
    def __init__(self, func):
        self.func = func
        self.__name__ = func.__name__
    def __call__(self, *args, **kwargs):
        return self.func.__call__(*args, **kwargs)

def view(pattern, template, form_cls = None, redirect_to = None, invalid_form_msg = 'Form is not valid.', **kwargs):
    class Wrapper(Decorator):
        def __init__(self, obj):
            super(Wrapper, self).__init__(obj)

            if isinstance(obj, types.ClassType):
                obj = obj()

            permitted_methods = {}

            for method in ('get','post', 'option', 'put', 'delete', 'head'):
                if hasattr(obj, method):
                    fnc = getattr(obj, method)
                    if not isinstance(fnc, types.FunctionType):
                        fnc = partial(fnc, obj)
                    permitted_methods[method.upper()] = fnc

                else:
                    # in case we have decorated function instead of class..
                    if hasattr(obj, '__call__'):
                        permitted_methods[method.upper()] = obj

            require_http_methods_decorator = http.require_http_methods(request_method_list=permitted_methods.keys())
            for key, val in  permitted_methods.items():
                setattr(self, key.lower(), require_http_methods_decorator(val))

        @staticmethod
        def _mk_forms(*args, **kwargs):
            if isinstance(form_cls,tuple):
                return tuple(f(*args, **kwargs) for f in form_cls)
            else:
                if form_cls is not None:
                    return form_cls(*args, **kwargs),
                else:
                    return None,

        def url(self):
            return url(pattern, self, kwargs, self.__name__)

        def __call__(self, request, *args, **kwargs):
            try:
                if request.method == 'POST':
                    ret =  self.post(request, *args, **kwargs)
                    forms = self._mk_forms(request.POST)
                    if not all(f.is_valid() for f in forms):
                        forms =  self._mk_forms()
                        messages.error(request, invalid_form_msg)

                elif request.method in ('GET', 'HEAD', 'OPTION', 'PUT', 'DELETE') :
                    ret =  self.get(request, *args, **kwargs)
                    forms =  self._mk_forms(request.GET)
                    if not all(f.is_valid() if f is not None else True for f in forms):
                        forms =  self._mk_forms()

                elif request.method in ('HEAD', 'OPTION', 'PUT', 'DELETE') :
                    ret =  {}  # not implemented yet
                    forms =  self._mk_forms()

                else:
                    return

            except AttributeError:
                return


            if isinstance(ret, HttpResponse):
                return ret
            context_vars = {
                'form': forms[0], # default form is first one
                'forms': forms,
                }
            context_vars.update(kwargs)
            if isinstance(ret,dict):
                context_vars.update(ret)

            if redirect_to:
                context_vars['template'] = template
                return redirect(redirect_to, *args, **context_vars)
            else:
                return render(request, template, context_vars)
    return Wrapper

def redirect(attr='next_url', fallback='/'):
    class Wrapper(Decorator):
        def __call__(self, request, *args, **kwargs):
            from django.shortcuts import redirect
            ret = super(Wrapper,self).__call__(request, *args, **kwargs)
            if attr in request.POST:
                next = request.POST.get(attr)
            else:
                next = request.GET.get(attr,fallback)
            return ret if ret else redirect(next)
    return Wrapper

def default_response(response_cls=HttpResponse):
    class Wrapper(Decorator):
        def __call__(self, request, *args, **kwargs):
            ret = super(Wrapper,self).__call__(request, *args, **kwargs)
            return ret if ret else response_cls()
    return Wrapper