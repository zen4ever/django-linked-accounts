from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.generic.simple import direct_to_template

import django.contrib.auth as auth

from linked_accounts.models import LinkedAccount
from linked_accounts.utils import get_profile
from linked_accounts.forms import RegisterForm


LINKED_ACCOUNTS_ID_SESSION = getattr(
    settings,
    'LINKED_ACCOUNTS_ID_SESSION',
    '_linked_acccount_id'
)


class AuthCallback(object):
    def __call__(self, request, access, token):
        next = request.POST.get('next', settings.LOGIN_REDIRECT_URL)
        service = access.service
        if request.user.is_authenticated():
            profile = get_profile(service=service, token=token)
            if not profile.user:
                profile.user = request.user
                profile.save()
            access.persist(request.user,
                           token,
                           identifier="auth")
        else:
            profile = auth.authenticate(service=service, token=token)
            if profile.user:
                auth.login(request, profile.user)
                access.persist(profile.user,
                               token,
                               identifier="auth")
            else:
                request.session[LINKED_ACCOUNTS_ID_SESSION] = profile.id
                return HttpResponseRedirect(
                    reverse('linked_accounts_register') + "?next=%s" % next
                )
        return HttpResponseRedirect(next)


def oauth_access_success(request, access, token):
    callback = AuthCallback()
    return callback(request, access, token)


def register(request, template_name="linked_accounts/registration.html"):
    next = request.REQUEST.get('next', settings.LOGIN_REDIRECT_URL)
    
    try:
        profile_id = request.session[LINKED_ACCOUNTS_ID_SESSION]
        profile = LinkedAccount.objects.get(id=profile_id)
    except (KeyError, LinkedAccount.DoesNotExist):
        return HttpResponseRedirect(next)

    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save(profile)
            auth.login(request, user)
            user.backend = "linked_accounts.backends.LinkedAccountsBackend"
            return HttpResponseRedirect(next)
    else:
        form = RegisterForm()
    return direct_to_template(
        request,
        template_name,
        {'form': form, 'profile': profile}
    )
