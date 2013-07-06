__author__ = 'pborky'

from django.contrib import messages
from django.shortcuts import redirect

from .forms import SearchForm, SiteContentForm, SiteContentReadOnlyForm, WhoisReadOnlyForm, IpReadOnlyForm
from project.helpers import view
from django.views.decorators import http, cache
from .models import SearchResult, SiteCategory, Search, Site, SIteContent, SiteAttributes

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
    r'^do/search$',
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
    form_cls = {'search':SearchForm },
    invalid_form_msg = 'You must select engine and enter query string.',
)
class search_results:
    @staticmethod
    def get(request, searchid, forms):
        search, = Search.objects.filter(id=int(searchid))
        forms['search'] = forms['search2'] = SearchForm(instance=search)
        details = {}
        for result in SearchResult.objects.filter(search=search):

            id = result.site.id, result.site.name, result.site.url

            content = SIteContent.objects.filter(site=result.site )
            if content:
                content = content.latest('date')
            else:
                content = None


            attributes = SiteAttributes.objects.filter(site=result.site )
            if attributes:
                attributes = attributes.latest('date')
            else:
                attributes = None

            details[id]= {
                'content_form': SiteContentForm(instance=content if content else SIteContent(site=result.site)) ,
                'content': SiteContentReadOnlyForm(instance=content) if content else None ,
                'whois': WhoisReadOnlyForm(instance=attributes.whois) if attributes else None,
                'ip': None,  # IpReadOnlyForm(instance=attributes.ip) if attributes else None,
                }

        return {
            'forms': forms,
            'results': SearchResult.objects.filter(search=search).order_by('sequence'),
            'categories': SiteCategory.objects.filter(active=True).order_by("id"),
            'details': details,
            }

@view(
    r'^edit/site_content$',
    redirect_to='search',
    redirect_attr='nexturl',
    form_cls = {'edit': SiteContentForm},
)
class site_edit:
    @staticmethod
    def post(request, forms):
        form = forms['edit']
        if not form.is_valid():
            return
        form.save()
        messages.success(request, 'Data successfuly saved.')

@view(
    r'^edit/site/banned$',
    redirect_to='search',
    redirect_attr='nexturl',
    form_cls = None,
)
class site_ban:
    @staticmethod
    def post(request, forms):
        site, = Site.objects.filter(id=int(request.POST['siteid']))
        site.banned = not site.banned
        site.save()
        if site.banned:
            messages.success(request, 'Site "%s" added to ban-list.' % (site.name,))
        else:
            messages.success(request, 'Site "%s" removed from ban-list.' % (site.name,))

@view(
    r'^scrap$',
    template = 'scrap.html',
)
class scrap:

    @staticmethod
    def get(request, *args, **kwargs):
        pass