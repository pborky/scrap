__author__ = 'pborky'

from django.contrib import messages
from django.shortcuts import redirect
from django.http import HttpResponseNotFound
from django.views.decorators import http, cache

from quirks.functional import maybe
from quirks.iterable import itake, first, imap

from .forms import SearchForm, SiteContentForm, SiteContentReadOnlyForm, WhoisReadOnlyForm, IpReadOnlyForm
from .models import SearchResult, SiteCategory, Search, Site, SIteContent, SiteAttributes, Keyword, Engine, Ip, Whois

from project.helpers import view
from project.addrutil import addrutil
from project.searches import google_search, root_page_keywords


def url_depath(url):
    from urlparse import urlsplit, urlunsplit
    scheme, netloc, _, _, _ = urlsplit(url)
    return urlunsplit((scheme, netloc, '/', '', ''))

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
    r'^search/do$',
    redirect_to='search_results',
    redirect_fallback = 'search',
    form_cls = {'search':SearchForm,},
    invalid_form_msg = 'You must select engine and enter query string.',
)
class search_submit:
    @staticmethod
    def post(request, forms):
        form = forms['search']
        if not form.is_valid():
            return {}
        data = form.data
        query = data.get('q')
        engine = data.get('engine')
        if query:
            engine = Engine.objects.get(id=engine)
            search = Search.objects.create(engine=engine, q=query)
            search.save()
            for res in itake(20, google_search(q=query)):
                res.update(addrutil(res['url'])) # add data from DNS & WHOIS
                bare_url = url_depath(res['url']) # remove path from url
                keywords = []
                category = None
                site = None
                try:
                    site = Site.objects.get(url=bare_url)
                except Exception:
                    pass

                if site:
                    # once processed in this run, we continue
                    if SearchResult.objects.filter(site=site, search=search):
                        continue


                if not site:
                    scraped_keywords = root_page_keywords(bare_url)
                    for kw in Keyword.objects.all():
                        if kw.keyword in scraped_keywords:
                            category = kw.category
                            keywords.append(kw)
                            break

                    site = Site(name=res.get('title'), url=bare_url, category=category, banned=False)
                    site.save()

                    site_attr = SiteAttributes(site=site)
                    site_attr.save()

                    ips = map(
                        lambda ip: Ip.objects.get_or_create(**ip)[0],
                        res.get('addresses',())
                    )
                    if ips:
                        site_attr.ip.add(*ips)
                        site_attr.save()
                    whois = map(
                        lambda whois: Whois.objects.get_or_create(**whois)[0],
                        res.get('whois',())
                    )
                    if whois:
                        site_attr.whois.add(*whois)

                search_result = SearchResult(search=search, sequence=res.get('_seq'), site=site)
                search_result.save()
                if keywords:
                    search_result.keyword.add(*keywords)
                search_result.save()
            return { 'searchid': search.id }
        else:
            return {}


@view(
    r'^search/(?P<searchid>\d*)$',
    template = 'search.html',
    form_cls = {'search':SearchForm },
    invalid_form_msg = 'You must select engine and enter query string.',
)
class search_results:
    @staticmethod
    def get(request, searchid, forms):

        try:
            search = Search.objects.get(id=int(searchid))
        except:
            return HttpResponseNotFound()

        forms['search'] = forms['search2'] = SearchForm(instance=search)
        details = {}
        for result in SearchResult.objects.filter(search=search):

            site = result.site
            id = site.id, site.name, site.url
            content = attributes = ip = whois = None

            try:
                content = SIteContent.objects.filter(site=site ).latest('date')
            except:
                pass

            try:
                attributes = SiteAttributes.objects.filter(site=site ).latest('date')
            except:
                pass

            if attributes:
                ip = first(attributes.ip.all())
                whois = first(attributes.whois.all())

            details[id]= {
                'content_form': None, # SiteContentForm(instance=content if content else SIteContent(site=result.site)) ,
                'content': None, #  SiteContentReadOnlyForm(instance=content) if content else None ,
                'whois': None, #  WhoisReadOnlyForm(instance=whois) if whois else None,
                'ip': None, #  IpReadOnlyForm(instance=ip) if ip else None,
                }

        return {
            'forms': forms,
            'results': SearchResult.objects.filter(search=search).order_by('sequence'),
            'categories': SiteCategory.objects.filter(active=True).order_by("id"),
            'details': details,
            }

def get_site_details(siteid):
    site = Site.objects.get(id=int(siteid))

    content = attributes = ip = whois = None

    try:
        content = SIteContent.objects.filter(site=site ).latest('date')
    except:
        pass

    try:
        attributes = SiteAttributes.objects.filter(site=site ).latest('date')
    except:
        pass

    if attributes:
        ip = first(attributes.ip.all())
        whois = first(attributes.whois.all())
    return site,content,whois,ip


@view(
    r'^site-content/(?P<siteid>\d*)/detail$',
    template = 'site-content-ajax.html',
)
class site_content_detail:
    @staticmethod
    def get(request, forms, siteid):
        nexturl = request.GET.get('nexturl')
        try:
            site,content,whois,ip = get_site_details(siteid)
        except:
            return HttpResponseNotFound()

        return {
            'edit': False,
            'site': site,
            'nexturl': nexturl,
            'detail': {
                'content':   SiteContentReadOnlyForm(instance=content) if content else SiteContentReadOnlyForm() ,
                'whois':   WhoisReadOnlyForm(instance=whois) if whois else WhoisReadOnlyForm(),
                'ip':   IpReadOnlyForm(instance=ip) if ip else IpReadOnlyForm(),
                }
        }
@view(
    r'^site-content/(?P<siteid>\d*)/edit$',
    template = 'site-content-ajax.html',
)
class site_content_edit:
    @staticmethod
    def get(request, forms, siteid):
        nexturl = request.GET.get('nexturl')
        try:
            site,content,whois,ip = get_site_details(siteid)
        except:
            return HttpResponseNotFound()

        return {
            'edit': True,
            'site': site,
            'nexturl': nexturl,
            'detail': {
                'content':  SiteContentForm(instance=content if content else SIteContent(site=site)) ,
                'whois':   WhoisReadOnlyForm(instance=whois) if whois else WhoisReadOnlyForm(),
                'ip':   IpReadOnlyForm(instance=ip) if ip else IpReadOnlyForm(),
                }
        }

@view(
    r'^site-content/edit$',
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
    r'^site/banned/edit$',
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