from django.db import models

class Engine(models.Model):
    name = models.CharField(max_length=100, unique=True)
    symbol = models.CharField(max_length=10, unique=True, null=True)
    active = models.BooleanField(default=False)
    def __unicode__(self):
        return self.name
    class Meta:
        ordering = ["name"]
        verbose_name = "Search engine"
        permissions = (("can_edit_engines", "Can edit search engines"),)
