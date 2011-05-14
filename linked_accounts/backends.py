from django.contrib.auth.models import User
from linked_accounts.handlers import AuthHandler


class LinkedAccountsBackend(object):

    def get_user(self, user_id):
        return User.objects.get(id=user_id)

    def authenticate(self, service=None, token=None):
        return AuthHandler.get_handler(service).get_profile(token)
