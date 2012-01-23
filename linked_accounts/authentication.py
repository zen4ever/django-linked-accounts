from django.http import HttpResponse
from django.template import loader
from django.utils.crypto import salted_hmac, constant_time_compare

from django.contrib.auth.models import User


class HMACAuth(object):

    def __init__(self, realm='API'):
        self.realm = realm

    def process_request(self, request):
        user_id = request.META.get('HTTP_X_LA_USER_ID', None)
        signature = request.META.get('HTTP_X_LA_HASH', None)
        return user_id, signature

    def is_authenticated(self, request):
        user_id, signature = self.process_request(request)

        if user_id and signature:
            check_digest = salted_hmac("linked_accounts.views.login", str(user_id)).hexdigest()
            if not constant_time_compare(signature, check_digest):
                return False

            try:
                user = User.objects.get(id=user_id)
                if user.is_active:
                    request.user = user
                    return True
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
