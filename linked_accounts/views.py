from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
import django.contrib.auth as auth

from linked_accounts.handlers import AuthHandler


LINKED_ACCOUNTS_ID_SESSION = getattr(
    settings,
    'LINKED_ACCOUNTS_ID_SESSION',
    '_linked_acccount_id'
)

LINKED_ACCOUNTS_NEXT_KEY = getattr(
    settings,
    'LINKED_ACCOUNTS_NEXT_KEY',
    'oauth_next'
)


class AuthCallback(object):
    def __call__(self, request, access, token):
        next_url = request.session.get(LINKED_ACCOUNTS_NEXT_KEY, settings.LOGIN_REDIRECT_URL)
        service = access.service
        if request.user.is_authenticated():
            profile = AuthHandler.get_handler(service).get_profile(token)
            if not profile.user:
                profile.user = request.user
                profile.save()
            access.persist(request.user,
                           token,
                           identifier="auth")
        else:
            profile = auth.authenticate(service=service, token=token)
            if profile.user:
                profile.user.backend = "linked_accounts.backends.LinkedAccountsBackend"
                auth.login(request, profile.user)
                access.persist(profile.user,
                               token,
                               identifier="auth")
            else:
                request.session[LINKED_ACCOUNTS_ID_SESSION] = profile.id
                return HttpResponseRedirect(
                    reverse('linked_accounts_register') + "?next=%s" % next_url
                )
        return HttpResponseRedirect(next_url)


def oauth_access_success(request, access, token):
    callback = AuthCallback()
    return callback(request, access, token)
