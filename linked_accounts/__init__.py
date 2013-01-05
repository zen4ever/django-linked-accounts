from django.conf import settings
from oauth_flow.handlers import get_handler

SETTINGS = getattr(settings, 'OAUTH_FLOW_SETTINGS', {})
HANDLERS = getattr(settings, 'OAUTH_FLOW_HANDLERS', None)


def get_oauth_handler(service, **kwargs):
    if HANDLERS and not 'handlers' in kwargs:
        kwargs['handlers'] = HANDLERS
    return get_handler(service, settings=SETTINGS, **kwargs)
