from quirks.iterable import isiterable,ifilter,imap,chain , ensure_iterable
from quirks.functional import maybe

import re
import datetime
from os import path

class _AddrUtil(object):
    def __init__(self, filename):
        import pygeoip
        # Load the database once and store it globally in interpreter memory.
        self.GEOIP = pygeoip.GeoIP(filename)
    def _get_domain(self, url):
        from urlparse import urlparse
        parsedurl = urlparse(url)
        return parsedurl.netloc
    def _get_geo_code(self, ip_address):
        if not hasattr(self, '_country_code_by_addr'):
            self._country_code_by_addr = maybe(self.GEOIP.country_code_by_addr)
        return self._country_code_by_addr(ip_address)
    def _resolve(self, domain):
        if not hasattr(self, 'query'):
            from dns.resolver import query
            self._query = ensure_iterable(maybe(query))
        return imap(str, ifilter(None, chain(self._query(domain, 'A'),self._query(domain, 'AAAA'))))
    def _get_ip_addresses(self, domain):
        import socket
        try:
            # try to resolve all A and AAAA records recursively
            return {
                'domain': domain,
                'addresses':[{ 'address': str(a), 'country': self._get_geo_code(a) } for a in self._resolve(domain)]
            }
        except:
            # fallback and resolve only one ip address
            return {
                'domain': domain,
                'addresses':[{ 'address': a, 'country': self._get_geo_code(a) } for a in socket.gethostbyname(domain)]
            }
    def _get_whois(self, domain):
        import whois

        pt1 = re.compile(r'(\w+):\s*(.*)\s*')
        pt2 = re.compile(r'(?P<day>\d+)[.](?P<month>\d+)[.](?P<year>\d+)\s+(?P<hour>\d+)[:](?P<minute>\d+)[:](?P<second>\d+)')
        try:
            e = whois.whois(domain)
            ATTR = ['address', 'name', 'registered']
            result = {}
            last_attr = None
            for key,value in pt1.findall(e.text):

                if key in ATTR:
                    if key in result:
                        if key != last_attr:
                            ATTR.pop(ATTR.index(key))
                            continue
                        result[key] += value,
                    else:
                        result[key] = [value,]
                last_attr = key
            #print  e,result
            return {
                'domain': domain,
                'whois': [
                    {
                    'contact': result['name'][0],
                    'address1': '; '.join(result['address'][:-1]),
                    'address2': result['address'][-1],
                    'date_from': datetime.datetime(**dict((k,int(v)) for k,v in pt2.match(result['registered'][0]).groupdict().items() )),
                    }
                ]
            }
        except:
            return {
                'domain': domain,
                }
    def __call__(self, url):
        domain = self._get_domain(url)
        return dict(chain(self._get_ip_addresses(domain).iteritems(), self._get_whois(domain).iteritems()))





addrutil = _AddrUtil(path.join(path.dirname(__file__), 'GeoIP.dat'))