__author__ = 'pborky'
__all__ = ['google_search', 'root_page']
from quirks.functional import partial, combinator
from quirks.iterable import itake

from .scraping import Chain, Form, Items, MySession , KeywordSet
from .addrutil import addrutil

import logging
logger = logging.getLogger(__name__)

class ScraperMetaclass(type):
    def __new__(mcs, name, bases, attrs):
        Meta = attrs.pop('Meta', None)
        scraping = getattr(Meta, 'scraping', None)
        session_init = getattr(Meta, 'session_init', {})
        #scrapping_init = getattr(Meta, 'scrapping_init', {})

        def _get_session(self, SessClass):
            return SessClass(**session_init)

        #def _scraping(self, session, *args, **kwargs):
        #    return scraping(session, **scrapping_init)

        attrs['_get_session'] = _get_session
        attrs['_scraping'] = scraping

        new_class = super(ScraperMetaclass, mcs).__new__(mcs, name, bases, attrs)
        return new_class

class Scraper(object):
    __metaclass__ =  ScraperMetaclass
    def __init__(self):
        super(Scraper,self).__init__()
        self._sess = self._get_session(MySession)
        #self._scraping = self._get_scrapping(self._sess)
    def __call__(self, *args, **kwargs):
        try:
            return self._scraping(self._sess, *args, **kwargs)
        except Exception as e:
            logger.error(e)
            logger.warning('Reloading webkit session.')
            try:
                self._sess.kill()
            except Exception:
                pass
            self._sess = self._get_session(MySession)
    def __del__(self):
        self._sess.kill()
        super(Scraper,self).__del__()

class GoogleSearch(Scraper):
    class Meta:
        scraping = Chain(
            Form('/',
                q = '//input[@name="q"]'
            ),
            Items(
                _li = '//li[@class="g"]//h3[@class="r"]/a',
                _next = '//a[@class="pn"]',
                url = lambda a: a.get_attr('href').decode('utf-8'),
                title = lambda a: a.text().decode('utf-8'),
            )
        )
        session_init = {
            'base_url': 'https://google.com/',
        }

class RootPage(Scraper):
    def __call__(self, url, *args, **kwargs):
        self._sess.base_url = url
        return super(RootPage, self).__call__(*args, **kwargs)
    class Meta:
        scraping = KeywordSet('/')

google_search = GoogleSearch()
engines = {
    'GOOG_S': google_search
}
root_page_keywords = RootPage()


