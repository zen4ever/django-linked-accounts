from django.core.management.base import NoArgsCommand
from linked_accounts.models import LinkedAccount


class Command(NoArgsCommand):
    help = "Convert RpxData profiles to LinkedAccount objects"

    def handle_noargs(self, *args, **kwargs):
        from django_rpx.models import RpxData
        for rpx in RpxData.objects.all():
            print rpx.provider
            identifier = None
            if rpx.provider == 'Facebook':
                _, identifier = rpx.identifier.split('=')
            elif rpx.provider == 'Google':
                identifier = rpx.user.email
            elif rpx.provider == 'Twitter':
                identifier = rpx.info_page_url.split('/')[-1]
            elif rpx.provider == 'Yahoo!':
                identifier = rpx.user.email
            if identifier:
                service = rpx.provider.lower().replace('!', '')
                if not LinkedAccount.objects.filter(identifier=identifier, service=service).exists():
                    linked_account, created = LinkedAccount.objects.get_or_create(
                        identifier=identifier,
                        service=service,
                        user=rpx.user,
                        picture_url=rpx.profile_pic_url,
                        info_page_url=rpx.info_page_url
                    )
