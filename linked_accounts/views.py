from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.generic.simple import direct_to_template

import django.contrib.auth as auth

from linked_accounts.models import LinkedAccount
from linked_accounts.handlers import AuthHandler
from linked_accounts.forms import RegisterForm


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


def login(request, template_name="linked_accounts/login.html"):
    next_url = request.REQUEST.get('next', settings.LOGIN_REDIRECT_URL)
    request.session[LINKED_ACCOUNTS_NEXT_KEY] = next_url
    return direct_to_template(request, template_name)


def register(request, template_name="linked_accounts/registration.html"):
    next_url = request.REQUEST.get('next', settings.LOGIN_REDIRECT_URL)
    
    try:
        profile_id = request.session[LINKED_ACCOUNTS_ID_SESSION]
        profile = LinkedAccount.objects.get(id=profile_id)
    except (KeyError, LinkedAccount.DoesNotExist):
        return HttpResponseRedirect(next_url)

    initial_data = {
        'username': profile.username
    }

    email = profile.email
    if email:
        initial_data['email'] = email

    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save(profile)
            user.backend = "linked_accounts.backends.LinkedAccountsBackend"
            auth.login(request, user)
            return HttpResponseRedirect(next_url)
    else:
        form = RegisterForm(initial=initial_data)

    return direct_to_template(
        request,
        template_name,
        {'form': form, 'profile': profile, 'next': next_url}
    )
