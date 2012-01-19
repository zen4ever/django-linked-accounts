from django.db import models
from django.utils import simplejson as json


class LinkedAccount(models.Model):
    identifier = models.CharField(max_length=255, db_index=True)
    service = models.CharField(max_length=255, db_index=True)
    user = models.ForeignKey('auth.User', null=True)
    api_response = models.TextField(default='', blank=True)

    picture_url = models.URLField(blank=True, verify_exists=False)
    info_page_url = models.URLField(blank=True, verify_exists=False)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    @property
    def api_response_data(self):
        return json.loads(self.api_response)

    def get_handler(self):
        from linked_accounts.handlers import AuthHandler
        return AuthHandler.get_handler(self.service)

    @property
    def username(self):
        return self.get_handler().get_username(self)

    @property
    def email(self):
        return self.get_handler().get_email(self)

    @property
    def emails(self):
        handler = self.get_handler()
        if hasattr(handler, 'get_emails'):
            return handler.get_emails(self)
        return filter(lambda x: x, [self.email])

    class Meta:
        unique_together = ('identifier', 'service')

    def __unicode__(self):
        return self.identifier
