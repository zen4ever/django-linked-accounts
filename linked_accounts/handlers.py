from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils import simplejson as json
from django.utils.importlib import import_module

from linked_accounts import get_oauth_handler


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

LINKED_ACCOUNTS_EMAIL_MATCH = getattr(
    settings,
    'LINKED_ACCOUNTS_EMAIL_MATCH',
    True
)


class AuthHandler(object):
    service = None
    profile_url = None
    identifier_name = None
    picture_name = None
    info_page_name = 'link'

    @classmethod
    def get_access(self, **kwargs):
        oauth_handler = get_oauth_handler(self.service, **kwargs)
        return oauth_handler

    @classmethod
    def get_picture_url(self, profile):
        data = self.get_data(profile)
        return data.get(self.picture_name, '')

    @classmethod
    def get_info_page_url(self, profile):
        data = self.get_data(profile)
        return data.get(self.info_page_name, '')

    @classmethod
    def get_profile_data(self, token, **kwargs):
        access = self.get_access(**kwargs)
        api_response = access.make_api_call("raw", self.profile_url, token)
        profile = json.loads(api_response)
        if isinstance(self.identifier_name, list):
            identifier = profile
            for name in self.identifier_name:
                identifier = identifier[name]
        else:
            identifier = profile[self.identifier_name]
        return identifier, api_response

    @classmethod
    def get_profile(self, token, **kwargs):

        identifier, api_response = self.get_profile_data(token, **kwargs)

        profile = json.loads(api_response)

        from linked_accounts.models import LinkedAccount

        account, update = None, True
        try:
            account = LinkedAccount.objects.get(
                identifier=identifier,
                service=self.service
            )
            if account.api_response:
                update = LINKED_ACCOUNTS_ALWAYS_UPDATE_PROFILE
        except LinkedAccount.DoesNotExist:
            if LINKED_ACCOUNTS_EMAIL_MATCH:
                emails = self.get_emails(profile)
                try:
                    account = LinkedAccount.objects.get(
                        identifier__in=emails,
                        service=self.service
                    )
                    account.identifier = identifier
                except LinkedAccount.DoesNotExist:
                    pass

        if not account:
            account = LinkedAccount.objects.create(
                identifier=identifier,
                service=self.service
            )

        if update:
            account.api_response = api_response
            account.picture_url = self.get_picture_url(profile)
            account.info_page_url = self.get_info_page_url(profile)
            account.save()
        return account

    @classmethod
    def get_data(self, profile):
        if isinstance(profile, dict):
            data = profile
        else:
            data = profile.api_response_data
        return data

    @classmethod
    def get_emails(self, profile):
        email = self.get_email(profile)
        if email:
            return [email]
        return []

    @classmethod
    def get_email(self, profile):
        data = self.get_data(profile)
        return data.get("email", None)

    @classmethod
    def get_first_name(self, profile):
        data = self.get_data(profile)
        return data.get(self.first_name, '')

    @classmethod
    def get_last_name(self, profile):
        data = self.get_data(profile)
        return data.get(self.last_name, '')

    @classmethod
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
    profile_url = "https://api.twitter.com/1.1/account/verify_credentials.json"
    identifier_name = "screen_name"
    picture_name = 'profile_image_url'

    @classmethod
    def get_first_name(self, profile):
        data = self.get_data(profile)
        name = data.get('name', '')
        parts = name.split(' ')
        if len(parts) == 2:
            return parts[0]
        elif len(parts) > 2:
            return " ".join(parts[:-1])
        return name

    @classmethod
    def get_last_name(self, profile):
        data = self.get_data(profile)
        name = data.get('name', '')
        parts = name.split(' ')
        if len(parts) == 2:
            return parts[1]
        elif len(parts) > 2:
            return parts[-1]
        return ''

    @classmethod
    def get_info_page_url(self, profile):
        data = self.get_data(profile)
        return "https://twitter.com/" + data[self.identifier_name]

    @classmethod
    def get_username(self, profile):
        data = self.get_data(profile)
        return data["screen_name"]


class FacebookHandler(AuthHandler):
    service = "facebook"
    profile_url = "https://graph.facebook.com/me"
    identifier_name = "id"
    first_name = 'first_name'
    last_name = 'last_name'

    @classmethod
    def get_picture_url(self, profile):
        data = self.get_data(profile)
        return "http://graph.facebook.com/%s/picture?type=large" % data[self.identifier_name]

    @classmethod
    def get_username(self, profile):
        data = self.get_data(profile)
        return (data["first_name"] + "_" + data["last_name"]).lower()


class GoogleHandler(AuthHandler):
    service = "google"
    profile_url = "https://www.googleapis.com/oauth2/v1/userinfo?alt=json"
    identifier_name = "id"
    picture_name = 'picture'
    first_name = 'given_name'
    last_name = 'family_name'

    @classmethod
    def get_username(self, profile):
        data = self.get_data(profile)
        return data["email"].split("@")[0]


class YahooHandler(AuthHandler):
    service = "yahoo"
    profile_url = "http://social.yahooapis.com/v1/me/guid?format=json"
    identifier_name = ["guid", "value"]
    info_page_name = "profileUrl"
    first_name = 'givenName'
    last_name = 'familyName'

    @classmethod
    def get_picture_url(self, profile):
        data = self.get_data(profile)
        return data.get('image', {}).get('imageUrl', '')

    @classmethod
    def get_emails(self, profile):
        data = self.get_data(profile)
        return [x['handle'] for x in data.get('emails', [])]

    @classmethod
    def get_email(self, profile):
        data = self.get_data(profile)
        primary = filter(lambda x: x.get('primary', False), data.get('emails', []))
        if primary:
            return primary[0]['handle']
        return ''

    @classmethod
    def get_username(self, profile):
        email = self.get_email(profile)
        if email:
            return email.split('@')[0]
        data = self.get_data(profile)
        return data["nickname"]

    @classmethod
    def get_profile_data(self, token, **kwargs):
        identifier, api_response = super(YahooHandler, self).get_profile_data(token, **kwargs)
        access = self.get_access(**kwargs)
        api_response = access.make_api_call(
            "raw",
            "http://social.yahooapis.com/v1/user/%s/profile?format=json" % identifier,
            token
        )
        profile = json.loads(api_response)
        return identifier, json.dumps(profile['profile'])


class LinkedInHandler(AuthHandler):
    service = "linkedin"
    profile_url = "http://api.linkedin.com/v1/people/~:(id,first-name,last-name,three-current-positions,picture-url,public-profile-url)?format=json"
    identifier_name = "id"
    picture_name = 'picture-url'
    info_page_name = 'public-profile-url'
    first_name = 'firstName'
    last_name = 'lastName'

    @classmethod
    def get_username(self, profile):
        data = self.get_data(profile)
        return data["firstName"] + "_" + data["lastName"]
