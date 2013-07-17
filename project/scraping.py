from webkit_server import InvalidResponseError

__author__ = 'pborky'

from dryscrape import Session

from quirks.iterable import isiterable, chain, imap
from quirks.functional import maybe, combinator, partial
import cssselect
from unicodedata import normalize
from unidecode import unidecode

from HTMLParser import HTMLParser

class HtmlTagStripper(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.reset()
        self.fed = []
        self.skip = {
            'script': 0,
            'style': 0,
        }
    def handle_starttag(self, tag, attrs):
        if tag in self.skip.keys():
            self.skip[tag] += 1
    def handle_endtag(self, tag):
        if tag in self.skip.keys():
            self.skip[tag] -= 1
    def handle_data(self, d):
        if not any(self.skip.values()):
            self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)
    @classmethod
    def strip(cls, html):
        s = cls()
        s.feed(html)
        return s.get_data()

class Scraping(object):
    pass

class KeywordSet(Scraping):
    def __init__(self, path, *args, **kwargs):
        self.path = path
    def __call__(self, session, *args, **kwargs):
        try:
            session.visit(self.path)
            session.wait()
            full_page = unidecode(session.body().decode('utf-8'))
            return  set(s.strip(' .,?!') for s in HtmlTagStripper.strip(full_page).lower().split())
        except InvalidResponseError as e:
            print 'InvalidResponseError:', e
        return set()

class Form(Scraping):
    def __init__(self, path, *args, **kwargs):
        self.path = path
        self.fields =  kwargs # xpaths of the fields
    def __call__(self, session, *args, **kwargs):
        session.visit(self.path)
        session.wait()
        forms = []
        for k,node in ( (k,session.at_xpath(v)) for k,v in self.fields.iteritems() ):
            node.set(kwargs.get(k))
            form = node.form()
            if form not in forms:
                forms.append(form)
        if  not forms or len (forms) > 1:
            raise Exception('You can submit only one form.')
        forms[0].submit()
        session.wait()


class Items(Scraping):
    def __init__(self, *args, **kwargs):
        self.fields =  kwargs
    def __call__(self, session, *args, **kwargs):
        return PageIterator(session, **self.fields)


class PageIterator(object):
    def __init__(self,  session, **fields):
        self.session = session
        self.next = fields.pop('_next', None)
        self.li = fields.pop('_li', None)
        #self.fields = fields # xpaths of the fields applied to li nodes
        self.fields = dict( (k,maybe(f)) if callable(f) else f for k,f in  fields.items() )
    @staticmethod
    def _value(node, selector):
        if callable(selector):
            return selector(node)
        else:
            xpath_or_css = maybe(node.at_xpath, node.at_css)
            return xpath_or_css(selector)
    @staticmethod
    def _values(node, selector):
        if callable(selector):
            res = (selector(node))
            return res if isiterable(res) else [res]
        else:
            xpath_or_css = maybe(node.xpath, node.css)
            return xpath_or_css(selector)
    @staticmethod
    def _mix(d, name, value):
        d[name] = value() if callable(value) else value
        return d
    def __iter__(self):
        from quirks.iterable import count
        from urlparse import urljoin
        seq = count()
        while True:
            current_url = self.session.url()
            absolute_url = lambda url: urljoin(current_url, url)
            process_values = combinator(
                lambda  (key, value): (key, absolute_url(value) if key == 'url' else value),
            )
            for result in self._values(self.session,self.li):
                yield dict( chain(
                    imap(process_values, ( (key,self._value(result, selector)) for key,selector in self.fields.iteritems() )),
                    ( ('_seq', seq.next()), ('_url', self.session.url()) )
                ) )
            if not self.next:
                return
            next = self._value(self.session,self.next)
            if not next:
                return
            next.click()
            self.session.wait()

class Chain(object):
    def __init__(self, *scrapings):
        self.scrapings = scrapings
    def __call__(self, session, *args, **kwargs):
        from itertools import ifilter, chain
        # lazily evaluate chained scrapings, filter out None results
        return chain.from_iterable(
            ifilter(None,
                (scrap(session, *args, **kwargs) for scrap in self.scrapings)
            )
        )

class MySession(Session):
    def __init__(self, proxy=None, *args, **kwargs):
        super(MySession, self).__init__(*args, **kwargs)
        self.driver.set_header('user-agent','Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.22 (KHTML, like Gecko) Ubuntu Chromium/25.0.1364.160 Chrome/25.0.1364.160 Safari/537.22')
        self.driver.set_header('accept-language', 'en-US,en;q=0.8,en-GB;q=0.6')
        self.driver.set_header('accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')
        self.set_error_tolerant(True)
        if proxy: self.set_proxy(*proxy) # tuple (host,port)