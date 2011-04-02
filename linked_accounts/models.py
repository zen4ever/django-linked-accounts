from django.db import models
from django.utils import simplejson as json


class LinkedAccount(models.Model):
    identifier = models.CharField(max_length=255, db_index=True)
    service = models.CharField(max_length=255, db_index=True)
    user = models.ForeignKey('auth.User', null=True)
    api_response = models.TextField(default='', blank=True)

    @property
    def api_response_data(self):
        return json.loads(self.api_response)

    class Meta:
        unique_together = ('identifier', 'service')

    def __unicode__(self):
        return self.identifier
