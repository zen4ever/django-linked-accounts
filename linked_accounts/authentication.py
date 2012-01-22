import base64
from django.http import HttpResponse
from django.template import loader
from django.utils.crypto import salted_hmac, constant_time_compare

from django.contrib.auth.models import User


class HMACAuth(object):

    def __init__(self, realm='API'):
        self.realm = realm

    def process_request(self, request):
        user_id = request.META.get('LA_USER_ID', None)
        signature = request.META.get('LA_HASH', None)
        return user_id, signature

    def is_authenticated(self, request):
        user_id, signature = self.process_request(request)
        digest = base64.decodestring(signature)
        check_digest = salted_hmac("linked_accounts.views.login", str(user_id))
        if not constant_time_compare(digest, check_digest):
            return False

        try:
            user = User.objects.get(id=user_id)
            if user.is_active:
                request.user = user
        except User.DoesNotExist:
            pass

        return False

    def challenge(self):
        response = HttpResponse()
        response.status_code = 401

        tmpl = loader.render_to_string('linked_accounts/api_challenge.html')

        response.content = tmpl

        return response

    def __repr__(self):
        return u'<HMACAuth: realm=%s>' % self.realm
