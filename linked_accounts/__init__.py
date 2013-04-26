from django.conf import settings
from oauth_flow.handlers import get_handler

SETTINGS = getattr(settings, 'OAUTH_FLOW_SETTINGS', {})
HANDLERS = getattr(settings, 'OAUTH_FLOW_HANDLERS', None)


def get_oauth_handler(service, **kwargs):
    if HANDLERS and not 'handlers' in kwargs:
        kwargs['handlers'] = HANDLERS
    oauth_settings = dict(SETTINGS)
    extra_settings = kwargs.pop('extra_settings', {})
    if service in oauth_settings:
        service_settings = oauth_settings[service]
        service_settings.update(extra_settings)
        oauth_settings[service] = service_settings
    return get_handler(service, settings=oauth_settings, **kwargs)
