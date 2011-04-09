from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module

from linked_accounts import LINKED_ACCOUNTS_HANDLERS


HANDLERS = getattr(
    settings,
    'LINKED_ACCOUNTS_HANDLERS',
    LINKED_ACCOUNTS_HANDLERS
)


def get_profile(service=None, token=None):
    handler_module = dict(HANDLERS).get(service, None)
    if handler_module:
        module, handler = handler_module.rsplit('.', 1)
        handler_class = getattr(import_module(module), handler)
        handler = handler_class()
        profile = handler.get_profile(token)
        return profile
    else:
        raise ImproperlyConfigured('No handler for service %s' % service)
