from datetime import datetime

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils import simplejson as json
from django.utils.importlib import import_module

from oauth_access.access import OAuthAccess, OAuth20Token


LINKED_ACCOUNTS_HANDLERS = (
    ('facebook', 'linked_accounts.handlers.FacebookHandler'),
    ('twitter', 'linked_accounts.handlers.TwitterHandler'),
    ('google', 'linked_accounts.handlers.GoogleHandler'),
    ('yahoo', 'linked_accounts.handlers.YahooHandler'),
    ('linkedin', 'linked_accounts.handlers.LinkedInHandler'),
)

LINKED_ACCOUNTS_ALWAYS_UPDATE_PROFILE = getattr(
    settings,
    'LINKED_ACCOUNTS_ALWAYS_UPDATE_PROFILE',
    False
)

HANDLERS = getattr(
    settings,
    'LINKED_ACCOUNTS_HANDLERS',
    LINKED_ACCOUNTS_HANDLERS
)


class AuthHandler(object):
    service = None
    profile_url = None
    identifier_name = None

    def get_access(self):
        return OAuthAccess(self.service)

    def get_profile(self, token, **kwargs):
        access = self.get_access()
        api_response = access.make_api_call("raw", self.profile_url, token)
        profile = json.loads(api_response)
        if isinstance(self.identifier_name, list):
            identifier = profile
            for name in self.identifier_name:
                identifier = identifier[name]
        else:
            identifier = profile[self.identifier_name]

        from linked_accounts.models import LinkedAccount
        account, created = LinkedAccount.objects.get_or_create(
            identifier=identifier,
            service=self.service
        )
        if created or settings.LINKED_ACCOUNTS_ALWAYS_UPDATE_PROFILE:
            account.api_response = api_response
            account.save()
        return account

    def get_email(self, profile):
        return profile.api_response_data.get("email", None)

    def get_username(self, profile):
        raise NotImplemented()

    @classmethod
    def get_handler(cls, service):
        handler_module = dict(HANDLERS).get(service, None)
        if handler_module:
            module, handler = handler_module.rsplit('.', 1)
            handler_class = getattr(import_module(module), handler)
            handler_instance = handler_class()
            return handler_instance
        raise ImproperlyConfigured('No handler for service %s' % service)


class TwitterHandler(AuthHandler):
    service = "twitter"
    profile_url = "https://twitter.com/account/verify_credentials.json"
    identifier_name = "screen_name"

    def get_username(self, profile):
        return profile.api_response_data["screen_name"]


class FacebookHandler(AuthHandler):
    service = "facebook"
    profile_url = "https://graph.facebook.com/me"
    identifier_name = "id"

    def get_username(self, profile):
        data = profile.api_response_data
        return data["first_name"] + "_" + data["last_name"]

    def get_profile(self, token, **kwargs):
        token = OAuth20Token(
            token=token,
            expires=(token.expires - datetime.now()).seconds
        )
        return super(FacebookHandler, self).get_profile(token, **kwargs)


class GoogleHandler(AuthHandler):
    service = "google"
    profile_url = "https://www.google.com/m8/feeds/contacts/default/full?max-results=0&alt=json"
    identifier_name = ["feed", "id", "$t"]

    def get_username(self, profile):
        data = profile.api_response_data
        return data["feed"]["id"]["$t"]


class YahooHandler(AuthHandler):
    service = "yahoo"
    profile_url = "http://social.yahooapis.com/v1/me/guid&format=json"
    identifier_name = ["guid", "value"]

    def get_username(self, profile):
        data = profile.api_response_data
        return data["nickname"]

    def get_profile(self, token, **kwargs):
        account = super(YahooHandler, self).get_profile(token, **kwargs)
        access = self.get_access()
        api_response = access.make_api_call(
            "raw",
            "http://social.yahooapis.com/v1/user/%s/profile&format=json" % account.identifier,
            token
        )
        account.api_response = api_response
        account.save()
        return account


class LinkedInHandler(AuthHandler):
    service = "linkedin"
    profile_url = "http://api.linkedin.com/v1/people/~:(id,first-name,last-name,three-current-positions,picture-url,public-profile-url)?format=json"
    identifier_name = "id"

    def get_username(self, profile):
        data = profile.api_response_data
        return data["firstName"]+"_"+data["lastName"]
