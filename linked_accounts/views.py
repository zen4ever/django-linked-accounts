from django.conf import settings
from django.http import HttpResponseRedirect

import django.contrib.auth as auth

from linked_accounts.utils import get_profile


class AuthCallback(object):
    def __call__(self, request, access, token):
        next = request.POST.get('next', settings.LOGIN_REDIRECT_URL)
        service = access.service
        if request.user.is_authenticated():
            profile = get_profile(service=service, token=token)
            if not profile.user:
                profile.user = request.user
                profile.save()
        else:
            profile = auth.authenticate(service=service, token=token)
            if profile.user:
                auth.login(request, profile.user)
        return HttpResponseRedirect(next)
