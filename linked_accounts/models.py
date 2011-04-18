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

    @property
    def username(self):
        data = self.api_response_data
        result = {
            "twitter": lambda x: x["screen_name"],
            "facebook": lambda x: x["first_name"] + "_" + x["last_name"],
            "yahoo": lambda x: x['nickname'],
            "google": lambda x: x["feed", "id", "$t"],
        }.get(self.service, lambda x: None)(data)

        return result

    @property
    def email(self):
        data = self.api_response_data
        result = {
            "facebook": lambda x: x["email"],
            "yahoo": lambda x: x['email'],
            "google": lambda x: x["email"],
        }.get(self.service, lambda x: None)(data)
        return result

    class Meta:
        unique_together = ('identifier', 'service')

    def __unicode__(self):
        return self.identifier
