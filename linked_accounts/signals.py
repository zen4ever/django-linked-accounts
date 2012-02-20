from django.dispatch.dispatcher import Signal

login_successful = Signal(providing_args=['profile'])
