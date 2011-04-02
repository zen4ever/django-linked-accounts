from django.conf import settings
from django.http import HttpResponseRedirect

import django.contrib.auth as auth


class AuthCallback(object):
    def __call__(self, request, access, token):
        next = request.POST.get('next', settings.LOGIN_REDIRECT_URL)
        service = access.service
        if request.user.is_authenticated():
            pass
        else:
            user = auth.authenticate(service=service, token=token)
            if user:
                auth.login(request, user)
        return HttpResponseRedirect(next)
