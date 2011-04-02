from django.contrib.auth.models import User

from linked_accounts.utils import get_profile


class LinkedAccountsBackend(object):

    def get_user(self, user_id):
        return User.objects.get(id=user_id)

    def authenticate(self, service=None, token=None):
        profile = get_profile(service, token)
        return profile
