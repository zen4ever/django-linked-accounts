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

LINKED_ACCOUNTS_ALLOW_REGISTRATION = getattr(
    settings,
    'LINKED_ACCOUNTS_ALLOW_REGISTRATION',
    True
)

LINKED_ACCOUNTS_ALLOW_LOGIN = getattr(
    settings,
    'LINKED_ACCOUNTS_ALLOW_LOGIN',
    True
)


class AuthCallback(object):
    def __call__(self, request, access, token):
        self.access = access
        self.request = request
        self.token = token
        if request.user.is_authenticated():
            self.connect_profile_to_user(self, request.user, access, token)
        else:
            profile = auth.authenticate(service=access.service, token=token)
            if profile.user and LINKED_ACCOUNTS_ALLOW_LOGIN:
                self.login(profile)
            elif LINKED_ACCOUNTS_ALLOW_REGISTRATION:
                return self.create_user(self, request, profile)
            else:
                return self.registration_closed()
        return HttpResponseRedirect(self.get_next_url())

    def get_next_url(self):
        return self.request.session.get(LINKED_ACCOUNTS_NEXT_KEY, settings.LOGIN_REDIRECT_URL)

    def create_user(self, profile):
        self.request.session[LINKED_ACCOUNTS_ID_SESSION] = profile.id
        return HttpResponseRedirect(
            reverse('linked_accounts_register') + "?next=%s" % self.get_next_url()
        )

    def login(self, profile):
        profile.user.backend = "linked_accounts.backends.LinkedAccountsBackend"
        auth.login(self.request, profile.user)
        self.access.persist(profile.user,
                            self.token,
                            identifier="auth")

    def registration_closed(self):
        return HttpResponseRedirect(
            reverse('linked_accounts_registration_closed')
        )

    def connect_profile_to_user(self):
        profile = AuthHandler.get_handler(self.access.service).get_profile(self.token)
        if not profile.user:
            profile.user = self.request.user
            profile.save()
        self.access.persist(self.request.user,
                            self.token,
                            identifier="auth")


def oauth_access_success(request, access, token):
    callback = AuthCallback()
    return callback(request, access, token)


def login(request, template_name="linked_accounts/login.html"):
    next_url = request.REQUEST.get('next', settings.LOGIN_REDIRECT_URL)
    request.session[LINKED_ACCOUNTS_NEXT_KEY] = next_url
    service = request.REQUEST.get('service', '')
    if service and service in settings.OAUTH_ACCESS_SETTINGS:
        return HttpResponseRedirect(
            reverse('oauth_access_login', args=[service])
        )
    if len(settings.OAUTH_ACCESS_SETTINGS) == 1:
        return HttpResponseRedirect(
            reverse('oauth_access_login', args=[settings.OAUTH_ACCESS_SETTINGS.keys()[0]])
        )
    return direct_to_template(request, template_name)


def registration_closed(request, template_name="linked_accounts/registration_closed.html"):
    return direct_to_template(request, template_name)


def register(request, form_class=RegisterForm, template_name="linked_accounts/registration.html"):
    if not LINKED_ACCOUNTS_ALLOW_REGISTRATION:
        return HttpResponseRedirect(
            reverse('linked_accounts_registration_closed')
        )
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
        form = form_class(request.POST)

        if form.is_valid():
            user = form.save(profile)
            user.backend = "linked_accounts.backends.LinkedAccountsBackend"
            auth.login(request, user)
            return HttpResponseRedirect(next_url)
    else:
        form = form_class(initial=initial_data)

    return direct_to_template(
        request,
        template_name,
        {'form': form, 'profile': profile, 'next': next_url}
    )
