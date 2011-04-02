from datetime import datetime

from oauth_access.access import OAuthAccess, OAuth20Token


class AuthHandler(object):
    service = None
    profile_url = None

    def get_access(self):
        return OAuthAccess(self.service)


class TwitterHandler(AuthHandler):
    service = "twitter"
    profile_url = "https://twitter.com/account/verify_credentials.json"

    def get_profile(self, token, **kwargs):
        access = self.get_access()
        profile = access.make_api_call("json", self.profile_url, token)


class FacebookHandler(AuthHandler):
    service = "facebook"
    profile_url = "https://graph.facebook.com/me"

    def get_profile(self, token, **kwargs):
        token = OAuth20Token(
            token=token,
            expires=(token.expires - datetime.now()).seconds
        )
        access = self.get_access()
        profile = access.make_api_call("json", self.profile_url, token)
