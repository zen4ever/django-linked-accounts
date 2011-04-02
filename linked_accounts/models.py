from django.db import models


class LinkedAccount(models.Model):
    identifier = models.CharField(max_length=255, db_index=True)
    service = models.CharField(max_length=255, db_index=True)
    user = models.ForeignKey('auth.User', null=True)
    api_response = models.TextField(default='', blank=True)

    class Meta:
        unique_together = ('identifier', 'service')

    def __unicode__(self):
        return self.identifier
