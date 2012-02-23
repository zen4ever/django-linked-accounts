from django.conf import settings
from emailconfirmation.models import EmailAddress

def create_email(user):
    if 'emailconfirmation' in settings.INSTALLED_APPS:
        email_address, created = EmailAddress.objects.get_or_create(
            user=user,
            email=user.email
        )
        if created:
            email_address.verified = True
            if not email_address.set_as_primary(conditional=True):
                email_address.save()
