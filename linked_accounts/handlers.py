from datetime import datetime

from django.utils import simplejson as json

from oauth_access.access import OAuthAccess, OAuth20Token

from linked_accounts.models import LinkedAccount


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
        account, created = LinkedAccount.objects.get_or_create(
            identifier = profile[self.identifier_name],
            service = self.service
        )
        if created:
            account.api_response = api_response
            account.save()
        return account


class TwitterHandler(AuthHandler):
    service = "twitter"
    profile_url = "https://twitter.com/account/verify_credentials.json"
    identifier_name = "screen_name"


class FacebookHandler(AuthHandler):
    service = "facebook"
    profile_url = "https://graph.facebook.com/me"
    identifier_name = "id"

    def get_profile(self, token, **kwargs):
        token = OAuth20Token(
            token=token,
            expires=(token.expires - datetime.now()).seconds
        )
        return super(FacebookHandler, self).get_profile(token, **kwargs)
