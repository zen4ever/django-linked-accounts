from django.contrib.auth.models import User
from linked_accounts.handlers import AuthHandler
from oauth_access.access import OAuth20Token


class LinkedAccountsBackend(object):

    supports_object_permissions = False
    supports_anonymous_user = False
    supports_inactive_user = False

    def get_user(self, user_id):
        return User.objects.get(id=user_id)

    def authenticate(self, service=None, token=None, expires=None):
        if not expires is None and isinstance(token, basestring):
            token = OAuth20Token(token, int(expires))
        return AuthHandler.get_handler(service).get_profile(token)
