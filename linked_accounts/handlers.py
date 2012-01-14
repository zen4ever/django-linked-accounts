from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils import simplejson as json
from django.utils.importlib import import_module


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

    def get_access(self, **kwargs):
        from oauth_flow.handlers import get_handler
        oauth_handler = get_handler(self.service, **kwargs)
        return oauth_handler

    def get_profile(self, token, **kwargs):
        access = self.get_access(**kwargs)
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
        if created or LINKED_ACCOUNTS_ALWAYS_UPDATE_PROFILE:
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
        return (data["first_name"] + "_" + data["last_name"]).lower()


class GoogleHandler(AuthHandler):
    service = "google"
    profile_url = "https://www.googleapis.com/oauth2/v1/userinfo?alt=json"
    identifier_name = "id"

    def get_username(self, profile):
        data = profile.api_response_data
        return data["email"].split("@")[0]


class YahooHandler(AuthHandler):
    service = "yahoo"
    profile_url = "http://social.yahooapis.com/v1/me/guid?format=json"
    identifier_name = ["guid", "value"]

    def get_emails(self, profile):
        data = profile.api_response_data
        emails = {}
        for x in data['profile']['emails']:
            if x.get('primary', False):
                emails['primary'] = x['handle']
            if x['handle'].endswith('@yahoo.com'):
                emails['yahoo'] = x['handle']
        return emails

    def get_email(self, profile):
        emails = self.get_emails(profile)
        return emails.get('primary', None)

    def get_username(self, profile):
        emails = self.get_emails(profile)
        if emails:
            if 'yahoo' in emails:
                return emails['yahoo'].split('@')[0]
            elif 'primary' in emails:
                return emails['primary'].split('@')[0]
        data = profile.api_response_data
        return data['profile']["nickname"]

    def get_profile(self, token, **kwargs):
        account = super(YahooHandler, self).get_profile(token, **kwargs)
        access = self.get_access()
        api_response = access.make_api_call(
            "raw",
            "http://social.yahooapis.com/v1/user/%s/profile?format=json" % account.identifier,
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
        return data["firstName"] + "_" + data["lastName"]
