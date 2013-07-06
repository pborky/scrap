from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Model, CharField, BooleanField, FloatField, URLField, ForeignKey, ManyToManyField,\
                            DateField, GenericIPAddressField, DateTimeField, IntegerField

def flag(obj, attr, true, false, none):
    return (true if getattr(obj,attr) else false) if hasattr(obj, attr) else none

def active_flag(obj, true = '', false = '-', none = ''):
    return flag(obj,'active', true, false, none)

def banned_flag(obj, true = '-', false = '', none = ''):
    return flag(obj,'banned', true, false, none)

class Engine(Model):
    name = CharField(max_length=100, verbose_name='Name of Search Engine', unique=True)
    symbol = CharField(max_length=10, verbose_name='Search Engine Code', unique=True)
    active = BooleanField(verbose_name='Active', default=False)
    def __unicode__(self):
        return u'%s %s' %(active_flag(self),  self.name,)
    class Meta:
        ordering = ["-active", "name"]
        verbose_name = "Search Engine"
        permissions = (("can_edit_engines", "Can edit search engines"),)

class SiteCategory(Model):
    name = CharField(max_length=100, verbose_name='Site Category', unique=True)
    symbol = CharField(max_length=10, verbose_name='Category Code', unique=True)
    default = BooleanField(verbose_name='Default', default=False)
    active = BooleanField(verbose_name='Active', default=False)
    def __unicode__(self):
        return u'%s %s' %(active_flag(self),  self.name,)
    class Meta:
        ordering = ["-active", "name"]
        verbose_name = "Site Category"
        verbose_name_plural = "Site Categories"

class SiteType(Model):
    name =  CharField(max_length=100, verbose_name='Shop Type', unique=True)
    symbol = CharField(max_length=10, verbose_name='Type Code', unique=True)
    active = BooleanField(verbose_name='Active', default=False)
    def __unicode__(self):
        return u'%s %s' %(active_flag(self),  self.name,)
    class Meta:
        ordering = ["-active", "name"]
        verbose_name = "Shop Type"

class ShipmentMethod(Model):
    name = CharField(max_length=100, verbose_name='Shipment Method', unique=True)
    symbol = CharField(max_length=10, verbose_name='Shipment Method Code', unique=True)
    active = BooleanField(verbose_name='Active', default=False)
    def __unicode__(self):
        return u'%s %s' %(active_flag(self),  self.name,)
    class Meta:
        ordering = ["-active", "name"]
        verbose_name = "Shipment Method"

class Keyword(Model):
    keyword =  CharField(verbose_name='Keyword',max_length=100, unique=True)
    prior = FloatField(verbose_name='Priror probability',validators=[MinValueValidator(0),MaxValueValidator(1)])
    posterior = FloatField(verbose_name='Posterior probability',validators=[MinValueValidator(0),MaxValueValidator(1)])
    category = ForeignKey(SiteCategory)
    active = BooleanField(verbose_name='Active', default=False)
    def __unicode__(self):
        return u'%s %s (%s)' %(active_flag(self),  self.keyword, unicode(self.category))
    class Meta:
        ordering = ["-active", "keyword"]
        verbose_name = "Keyword"

class Site(Model):
    name = CharField(max_length=100, verbose_name='Name of Site', unique=True)
    url = URLField(verbose_name='URL of Site', unique=True)
    category = ForeignKey(SiteCategory, verbose_name='Category of Site')
    banned = BooleanField(verbose_name='Banned')
    def __unicode__(self):
        return u'%s %s (%s)' %(banned_flag(self),self.name, self.url)
    class Meta:
        ordering = ["banned", "name"]
        verbose_name = "Site"

class Whois(Model):
    contact = CharField(max_length=100, verbose_name='Contact')
    address1 = CharField(max_length=100, verbose_name='City Address')
    address2 = CharField(max_length=100, verbose_name='Country Address')
    date_from = DateField(verbose_name='Registration Date')
    def __unicode__(self):
        return u'%s' % self.contact
    class Meta:
        ordering = ["contact"]
        verbose_name = "Whois"
        verbose_name_plural = "Whois"

class Ip(Model):
    address = GenericIPAddressField(verbose_name='IP Address')
    country = CharField(max_length=10, verbose_name='Country Code')
    def __unicode__(self):
        return u'%s (%s)' %(self.country, unicode(self.address))
    class Meta:
        ordering = ["country", "address"]
        verbose_name = "IP Address"
        verbose_name_plural = "IP Addresses"

class SiteAttributes(Model):
    date = DateTimeField(verbose_name='Date of Check',auto_now=True)
    site = ForeignKey(Site)
    ip = ManyToManyField(Ip)
    whois = ForeignKey(Whois)
    def __unicode__(self):
        return u'%s (%s)' %(self.site, self.date)
    class Meta:
        ordering = ["site", "date"]
        verbose_name = "Site Attributes Check"

class SIteContent(Model):
    date = DateTimeField(verbose_name='Date of Check',auto_now=True)
    site = ForeignKey(Site)
    last_update = DateTimeField(verbose_name='Last Update Date', default=None, null=True, blank=True)
    shipment = ManyToManyField(ShipmentMethod)
    type = ForeignKey(SiteType, null=True, blank=True)
    links = ManyToManyField(Site, null=True, blank=True, related_name='link_sites')
    def __unicode__(self):
        return u'%s (%s)' %(self.site, self.date)
    class Meta:
        ordering = ["site", "date"]
        verbose_name = "Site Content Check"

class Search(Model):
    date = DateTimeField(verbose_name='Date of Search',auto_now=True)
    engine = ForeignKey(Engine)
    q = CharField(max_length=100, verbose_name='Search String')
    def __unicode__(self):
        return u'"%s" with %s (%s)' %(self.q, self.engine, self.date)
    class Meta:
        ordering = ["date"]
        verbose_name = "Search"
        verbose_name_plural = "Searches"


class SearchResult(Model):
    search = ForeignKey(Search)
    sequence = IntegerField(verbose_name='Sequence Number')
    keyword = ForeignKey(Keyword)
    site = ForeignKey(Site)
    def __unicode__(self):
        return u'%s (%s)' %(self.site, self.search.date)
    class Meta:
        ordering = ["site", "search"]
        verbose_name = "Search Result"
