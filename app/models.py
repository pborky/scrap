from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

class Helper(object):
    def flag(self, attr, true, false, none):
        return (true if getattr(self,attr) else false) if hasattr(self, attr) else none

    def active_flag(self, true = '', false = '-', none = ''):
        return self.flag('active', true, false, none)

    def banned_flag(self, true = '-', false = '', none = ''):
        return self.flag('banned', true, false, none)

class Engine(models.Model, Helper):
    name = models.CharField(max_length=100, verbose_name='Name of Search Engine', unique=True)
    symbol = models.CharField(max_length=10, verbose_name='Search Engine Code', unique=True)
    active = models.BooleanField(verbose_name='Active', default=False)
    def __unicode__(self):
        return u'%s %s' %(self.active_flag(),  self.name,)
    class Meta:
        ordering = ["-active", "name"]
        verbose_name = "Search Engine"
        permissions = (("can_edit_engines", "Can edit search engines"),)

class SiteCategory(models.Model, Helper):
    name = models.CharField(max_length=100, verbose_name='Site Category', unique=True)
    symbol = models.CharField(max_length=10, verbose_name='Category Code', unique=True)
    default = models.BooleanField(verbose_name='Default', default=False)
    active = models.BooleanField(verbose_name='Active', default=False)
    def __unicode__(self):
        return u'%s %s' %(self.active_flag(),  self.name,)
    class Meta:
        ordering = ["-active", "name"]
        verbose_name = "Site Category"
        verbose_name_plural = "Site Categories"

class SiteType(models.Model, Helper):
    name =  models.CharField(max_length=100, verbose_name='Shop Type', unique=True)
    symbol = models.CharField(max_length=10, verbose_name='Type Code', unique=True)
    active = models.BooleanField(verbose_name='Active', default=False)
    def __unicode__(self):
        return u'%s %s' %(self.active_flag(),  self.name,)
    class Meta:
        ordering = ["-active", "name"]
        verbose_name = "Shop Type"

class ShipmentMethod(models.Model, Helper):
    name = models.CharField(max_length=100, verbose_name='Shipment Method', unique=True)
    symbol = models.CharField(max_length=10, verbose_name='Shipment Method Code', unique=True)
    active = models.BooleanField(verbose_name='Active', default=False)
    def __unicode__(self):
        return u'%s %s' %(self.active_flag(),  self.name,)
    class Meta:
        ordering = ["-active", "name"]
        verbose_name = "Shipment Method"

class Keyword(models.Model, Helper):
    keyword =  models.CharField(verbose_name='Keyword',max_length=100, unique=True)
    prior = models.FloatField(verbose_name='Priror probability',validators=[MinValueValidator(0),MaxValueValidator(1)])
    posterior = models.FloatField(verbose_name='Posterior probability',validators=[MinValueValidator(0),MaxValueValidator(1)])
    category = models.ForeignKey(SiteCategory)
    active = models.BooleanField(verbose_name='Active', default=False)
    def __unicode__(self):
        return u'%s %s (%s)' %(self.active_flag(),  self.keyword, unicode(self.category))
    class Meta:
        ordering = ["-active", "keyword"]
        verbose_name = "Keyword"

class Site(models.Model, Helper):
    name = models.CharField(max_length=100, verbose_name='Name of Site', unique=True)
    url = models.URLField(verbose_name='URL of Site', unique=True)
    category = models.ForeignKey(SiteCategory, verbose_name='Category of Site')
    banned = models.BooleanField(verbose_name='Banned')
    def __unicode__(self):
        return u'%s %s (%s)' %(self.banned_flag(),self.name, self.url)
    class Meta:
        ordering = ["banned", "name"]
        verbose_name = "Site"

class Whois(models.Model):
    contact = models.CharField(max_length=100, verbose_name='Contact')
    address1 = models.CharField(max_length=100, verbose_name='City Address')
    address2 = models.CharField(max_length=100, verbose_name='Country Address')
    date_from = models.DateField(verbose_name='Registration Date')
    def __unicode__(self):
        return u'%s' % self.contact
    class Meta:
        ordering = ["contact"]
        verbose_name = "Whois"
        verbose_name_plural = "Whois"

class Ip(models.Model):
    address = models.GenericIPAddressField(verbose_name='IP Address')
    country = models.CharField(max_length=10, verbose_name='Country Code')
    def __unicode__(self):
        return u'%s (%s)' %(self.country, unicode(self.address))
    class Meta:
        ordering = ["country", "address"]
        verbose_name = "IP Address"
        verbose_name_plural = "IP Addresses"


class SiteAttributes(models.Model):
    date = models.DateTimeField(verbose_name='Date of Check',auto_now=True)
    site = models.ForeignKey(Site)
    ip = models.ManyToManyField(Ip)
    whois = models.ForeignKey(Whois)
    def __unicode__(self):
        return u'%s (%s)' %(self.site, self.date)
    class Meta:
        ordering = ["site", "date"]
        verbose_name = "Site Attributes Check"

class SIteContent(models.Model):
    date = models.DateTimeField(verbose_name='Date of Check',auto_now=True)
    site = models.ForeignKey(Site)
    last_update = models.DateTimeField(verbose_name='Last Update Date', default=None, null=True, blank=True)
    shipment = models.ManyToManyField(ShipmentMethod)
    shipment.help_text=''  # TODO: this is crap
    type = models.ForeignKey(SiteType, null=True, blank=True)
    links = models.ManyToManyField(Site, null=True, blank=True, related_name='link_sites')
    links.help_text=''  # TODO: this is crap
    def __unicode__(self):
        return u'%s (%s)' %(self.site, self.date)
    class Meta:
        ordering = ["site", "date"]
        verbose_name = "Site Content Check"

class Search(models.Model):
    date = models.DateTimeField(verbose_name='Date of Search',auto_now=True)
    engine = models.ForeignKey(Engine)
    q = models.CharField(max_length=100, verbose_name='Search String')
    def __unicode__(self):
        return u'"%s" with %s (%s)' %(self.q, self.engine, self.date)
    class Meta:
        ordering = ["date"]
        verbose_name = "Search"
        verbose_name_plural = "Searches"


class SearchResult(models.Model):
    search = models.ForeignKey(Search)
    sequence = models.IntegerField(verbose_name='Sequence Number')
    keyword = models.ForeignKey(Keyword)
    site = models.ForeignKey(Site)
    def __unicode__(self):
        return u'%s (%s)' %(self.site, self.search.date)
    class Meta:
        ordering = ["site", "search"]
        verbose_name = "Search Result"
