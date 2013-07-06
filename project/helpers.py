from bootstrap_toolkit.widgets import add_to_css_class
from django.forms import TextInput
from django.utils.safestring import mark_safe

__author__ = 'pborky'


import types

from django.contrib import messages
from django.views.decorators import http, cache
from django.http import HttpResponse, HttpResponseServerError
from django.conf.urls import patterns, include, url

from functional import combinator,partial,flip

from django.db.models import get_models, get_app
from django.contrib import admin
from django.contrib.admin.sites import AlreadyRegistered
from django.forms.models import ModelFormMetaclass, ModelForm

def autoregister(*app_list):
    for app_name in app_list:
        app_models = get_app(app_name)
        for model in get_models(app_models):
            try:
                admin.site.register(model)
            except AlreadyRegistered:
                pass


class Decorator(object):
    def __init__(self, func):
        self.func = func
        self.__name__ = func.__name__
    def __call__(self, *args, **kwargs):
        return self.func.__call__(*args, **kwargs)

def view(pattern, template = None, form_cls = None, redirect_to = None, redirect_attr = None, invalid_form_msg = 'Form is not valid.', **kwargs):
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

            self.permitted_methods = permitted_methods.keys()

        @staticmethod
        def _mk_forms(*args, **kwargs):
            if isinstance(form_cls,tuple) or isinstance(form_cls, list):
                return list(f(*args, **kwargs) for f in form_cls)
            elif isinstance(form_cls, dict):
                return dict((k,f(*args, **kwargs)) for k,f in form_cls.iteritems())
            else:
                if form_cls is not None:
                    return [form_cls(*args, **kwargs),]
                else:
                    return [None,]
        @staticmethod
        def _is_valid(forms):
            if isinstance(forms,dict):
                it = forms.itervalues()
            else:
                it = forms
            return all(f.is_valid() if f is not None else True for f in it)
        def url(self):
            return url(pattern, self, kwargs, self.__name__)

        def __call__(self, request, *args, **kwargs):
            from django.shortcuts import render, redirect
            try:

                if not request.method in self.permitted_methods:
                    return http.HttpResponseNotAllowed(permitted_methods=self.permitted_methods)

                if request.method in ('POST',):

                    forms = self._mk_forms(request.POST)
                    ret =  self.post(request, *args, forms=forms, **kwargs)

                    if isinstance(ret, HttpResponse):
                        return ret

                    if not self._is_valid(forms) and invalid_form_msg:
                        messages.error(request, invalid_form_msg)

                elif request.method in ('GET',) :

                    forms =  self._mk_forms(request.GET) if request.GET else self._mk_forms()

                    ret =  self.get(request, *args, forms=forms, **kwargs)

                    if isinstance(ret, HttpResponse):
                        return ret

                    if not self._is_valid(forms):
                        #forms =  self._mk_forms()
                        #messages.error(request, invalid_form_msg)
                        pass

                elif request.method in ('HEAD', 'OPTION', 'PUT', 'DELETE') :
                    ret =  {}  # not implemented yet
                    forms =  self._mk_forms()

                else:
                    return

            except AttributeError as e:
                raise e
                #return HttpResponseServerError()

            redirect_addr = request.GET[redirect_attr] if redirect_attr in request.GET else redirect_to

            if redirect_addr:
                context_vars = { }

                context_vars.update(kwargs)

                if isinstance(ret,dict):
                    context_vars.update(ret)

                return redirect(redirect_addr, *args, **context_vars)
            else:
                context_vars = {
                            'forms': forms,
                        }
                context_vars.update(kwargs)

                if isinstance(ret,dict):
                    context_vars.update(ret)

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


class FormfieldCallback(object):

    def __init__(self, meta=None, **kwargs):
        if meta is None:
            self.attrs = {}
        elif isinstance(meta, dict):
            self.attrs = meta
        elif hasattr(meta, 'attrs'):
            self.attrs = meta.attrs
        else:
            raise TypeError('Argument "meta" must be dict or must contain attibute "attrs".')
        self.attrs.update(kwargs)

    def __call__(self, field, **kwargs):
        if field.name in self.attrs:
            kwargs.update(self.attrs[field.name])
        queryset_transform = kwargs.pop('queryset_transform', None)
        if callable(queryset_transform):
            pass #field.choices = queryset_transform(field.choices)
        return field.formfield(**kwargs)

class RichModelFormMetaclass(ModelFormMetaclass):
    def __new__(mcs, name, bases, attrs):
        Meta = attrs.get('Meta', None)
        attributes = getattr(Meta, 'attrs', {}) if Meta else {}

        if not attrs.has_key('formfield_callback'):
            attrs['formfield_callback'] = FormfieldCallback(**attributes)
        new_class = super(RichModelFormMetaclass, mcs).__new__(mcs, name, bases, attrs)
        return new_class

class ModelForm(ModelForm):
    __metaclass__ =  RichModelFormMetaclass
    def __init__ (self, *args, **kwargs):
        super(ModelForm,self).__init__ (*args, **kwargs)
        pass


class Uneditable(TextInput):
    def __init__(self, value_calback=None, choices=(), *args,  **kwargs):
        super(Uneditable, self).__init__(*args, **kwargs)
        self.value_calback = value_calback
        self.choices = list(choices)
        self.attrs['disabled'] = True

    def render(self, name, value, attrs=None):
        if attrs is None:
            attrs = {}
        attrs['type'] = 'hidden'
        klass = add_to_css_class(self.attrs.pop('class', ''), 'uneditable-input')
        klass = add_to_css_class(klass, attrs.pop('class', ''))

        base = super(Uneditable, self).render(name, value, attrs)
        if not isinstance(value, list):
            value = [value]
        if self.value_calback:
            if not hasattr(self, 'choices') or isinstance(self.choices, list):
                value = self.value_calback(None, value)
            else:
                value = self.value_calback(self.choices.queryset, value)
        return mark_safe(base + u'<span class="%s" style="color: #555555; background-color: #eeeeee;" disabled="true">%s</span>' % (klass, value))