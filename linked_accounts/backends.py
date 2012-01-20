from django.contrib.auth.models import User

from linked_accounts.handlers import AuthHandler

from oauth_flow.handlers import OAuth20Token


class LinkedAccountsBackend(object):

    supports_object_permissions = False
    supports_anonymous_user = False
    supports_inactive_user = False

    def get_user(self, user_id):
        return User.objects.get(id=user_id)

    def authenticate(self, service=None, token=None, expires=None):
        if isinstance(token, basestring) and service in ['facebook', 'google']:
            token = OAuth20Token(token, expires)
        handler = AuthHandler.get_handler(service)
        return handler.get_profile(token)
