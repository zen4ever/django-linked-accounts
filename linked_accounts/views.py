from django.conf import settings
from django.db import transaction
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils import simplejson as json
from django.utils.crypto import salted_hmac
from django.views.decorators.csrf import csrf_exempt

import django.contrib.auth as auth
from django.contrib.auth.models import User

from linked_accounts.forms import RegisterForm
from linked_accounts.handlers import AuthHandler
from linked_accounts.models import LinkedAccount
from linked_accounts.signals import login_successful

from linked_accounts import get_oauth_handler

try:
    from linked_accounts.utils import create_email
except ImportError:
    create_email = lambda x: None


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

LINKED_ACCOUNTS_AUTO_REGISTRATION = getattr(
    settings,
    'LINKED_ACCOUNTS_AUTO_REGISTRATION',
    True
)

LINKED_ACCOUNTS_EMAIL_ASSOCIATION = getattr(
    settings,
    'LINKED_ACCOUNTS_EMAIL_ASSOCIATION',
    False
)

LINKED_ACCOUNTS_ALLOW_LOGIN = getattr(
    settings,
    'LINKED_ACCOUNTS_ALLOW_LOGIN',
    True
)


def permute_name(name_string, num):
    num_str=str(num)
    max_len=29-len(num_str)
    return ''.join([name_string[0:max_len], '_', num_str])


class AuthCallback(object):
    def __call__(self, request, access, token, api=False):
        self.access = access
        self.request = request
        self.token = token
        self.api = api
        profile = None
        user = None
        try:
            user = request.user
        except User.DoesNotExist:
            pass
        if user and user.is_authenticated():
            profile = self.link_profile_to_user()
        else:
            profile = auth.authenticate(service=access.SERVICE, token=token)
            if profile.user:
                if LINKED_ACCOUNTS_ALLOW_LOGIN:
                    self.login(profile)
            elif LINKED_ACCOUNTS_ALLOW_REGISTRATION:
                return self.create_user(profile)
            else:
                return self.registration_closed()
        return self.success(profile)

    def success(self, profile):
        login_successful.send(sender=LinkedAccount, profile=profile)
        if self.api:
            result = {}
            if profile and profile.user:
                user_id = profile.user.id
                result['user_id'] = user_id
                signature = salted_hmac("linked_accounts.views.login", str(user_id)).hexdigest()
                result['hash'] = signature
                result['username'] = profile.user.username

            return HttpResponse(
                json.dumps(result),
                mimetype="application/json"
            )
        return redirect(self.get_next_url())

    def get_next_url(self):
        return self.request.session.get(
            LINKED_ACCOUNTS_NEXT_KEY,
            settings.LOGIN_REDIRECT_URL
        )

    def create_user(self, profile):
        if LINKED_ACCOUNTS_EMAIL_ASSOCIATION and profile.email:
            users = list(User.objects.filter(email=profile.email))
            if users and len(users) == 1:
                user = users[0]
                profile.user = user
                profile.save()
                create_email(user)
                if LINKED_ACCOUNTS_ALLOW_LOGIN:
                    self.login(profile)
                return self.success(profile)

        if LINKED_ACCOUNTS_AUTO_REGISTRATION:
            #no match, create a new user - but there may be duplicate user names.
            nickname = profile.username
            username = nickname
            user = None
            try:
                i=0
                while True:
                    User.objects.get(username=username)
                    username=permute_name(nickname, i)
                    i+=1
            except User.DoesNotExist:
                #available name!
                user = User.objects.create_user(username, profile.email or '')
                create_email(user)

            profile.user = user
            profile.save()
            if LINKED_ACCOUNTS_ALLOW_LOGIN:
                self.login(profile)
            return self.success(profile)
        else:
            self.request.session[LINKED_ACCOUNTS_ID_SESSION] = profile.id
            return redirect(
                reverse('linked_accounts_register') + "?next=%s" % self.get_next_url()
            )

    def login(self, profile):
        profile.user.backend = "linked_accounts.backends.LinkedAccountsBackend"
        auth.login(self.request, profile.user)

    def registration_closed(self):
        return redirect('linked_accounts_registration_closed')

    def link_profile_to_user(self):
        profile = AuthHandler.get_handler(self.access.SERVICE).get_profile(self.token)
        if not profile.user:
            profile.user = self.request.user
            profile.save()
        return profile


def authentication_complete(request, access, token):
    callback = AuthCallback()
    return callback(request, access, token)


def login(request, service=None, template_name="linked_accounts/login.html"):
    next_url = request.REQUEST.get('next', settings.LOGIN_REDIRECT_URL)
    request.session[LINKED_ACCOUNTS_NEXT_KEY] = next_url
    if service:
        oauth_handler = get_oauth_handler(
            service,
            request=request,
            redirect=reverse('linked_accounts_complete', args=[service])
        )
        return redirect(oauth_handler.auth_url())
    return render(request, template_name, {
        'next': next_url,
        'service': service,
    })


@transaction.commit_on_success
@csrf_exempt
def auth_complete(request, service=None):
    oauth_handler = get_oauth_handler(
        service,
        request=request,
        redirect=reverse('linked_accounts_complete', args=[service])
    )
    api = False
    if request.method == 'POST':
        data = json.loads(request.raw_post_data)
        access_token = data['token']
        api = True
    else:
        access_token = oauth_handler.auth_complete()
    callback = AuthCallback()
    return callback(request, oauth_handler, access_token, api=api)


def registration_closed(request, template_name="linked_accounts/registration_closed.html"):
    return render(request, template_name)


def register(request, form_class=RegisterForm, template_name="linked_accounts/registration.html"):
    if not LINKED_ACCOUNTS_ALLOW_REGISTRATION:
        return redirect('linked_accounts_registration_closed')
    next_url = request.REQUEST.get('next', settings.LOGIN_REDIRECT_URL)

    try:
        profile_id = request.session[LINKED_ACCOUNTS_ID_SESSION]
        profile = LinkedAccount.objects.get(id=profile_id)
    except (KeyError, LinkedAccount.DoesNotExist):
        return redirect(next_url)

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
            create_email(user)
            user.backend = "linked_accounts.backends.LinkedAccountsBackend"
            auth.login(request, user)
            return redirect(next_url)
    else:
        form = form_class(initial=initial_data)

    return render(
        request,
        template_name,
        {'form': form, 'profile': profile, 'next': next_url}
    )
