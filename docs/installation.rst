============
Installation
============

Dependencies
============

Django Linked Accounts depends on Eldarion's django-oauth-access,
if you need support for Google Accounts, you will need to install my fork of
it. You can run following commands through "pip install" to install necessary
dependencies:

::

    -e git://github.com/zen4ever/django-oauth-access.git@google#egg=django-oauth-access
    httplib2>=0.6.0
    oauth2>=1.5.167

Or use supplied "requirements.txt" file:

::
    git clone git://github.com/zen4ever/django-linked-accounts.git
    cd django-linked-accounts/
    pip install -r requirements.txt

App installation
================

Then you can install linked accounts themselves:

::

    pip install -e git://github.com/zen4ever/django-linked-accounts.git

Usage
=====

Add oauth_access and linked_accounts to your ``INSTALLED_APPS``:

.. code-block:: python

    INSTALLED_APPS = [
        # ...
        "oauth_access",
        "linked_accounts",
    ]

Hook them up to your URLconf:

.. code-block:: python

    urlpatterns = patterns("",
        # ...
        url(r"^oauth/", include("oauth_access.urls"))
        url(r"^linked_accounts/", include("linked_accounts.urls"))
    )

You would probably want to add linked_accounts auth backend to you
``AUTHENTICATION_BACKENDS``:

.. code-block:: python

    AUTHENTICATION_BACKENDS = (
        'django.contrib.auth.backends.ModelBackend',
        'linked_accounts.backends.LinkedAccountsBackend',
    )

Then you need to add OAuth settings for each service you want to use. Here is
a basic skeleton for supported services. To obtain ``KEY`` and ``SECRET`` you
will have to register an application with each service:

.. code-block:: python

    OAUTH_ACCESS_SETTINGS = {
        'linkedin': {
            'keys': {
                'KEY': '',
                'SECRET': '',
            },
            'endpoints': {
                'request_token': 'https://api.linkedin.com/uas/oauth/requestToken',
                'access_token': 'https://api.linkedin.com/uas/oauth/accessToken',
                'authorize': 'https://api.linkedin.com/uas/oauth/authenticate',
                'callback': 'linked_accounts.views.oauth_access_success',
                'provider_scope': [],
            },
        },
        'google': {
            'keys': {
                'KEY': '',
                'SECRET': '',
            },
            'endpoints': {
                'request_token': 'https://www.google.com/accounts/OAuthGetRequestToken',
                'access_token': 'https://www.google.com/accounts/OAuthGetAccessToken',
                'authorize': 'https://www.google.com/accounts/OAuthAuthorizeToken',
                'callback': 'linked_accounts.views.oauth_access_success',
                'provider_scope': ["http://www.google.com/m8/feeds/"],
            },
        },

        'yahoo': {
            'keys': {
                'KEY': '',
                'SECRET': '',
            },
            'endpoints': {
                'request_token': 'https://api.login.yahoo.com/oauth/v2/get_request_token',
                'access_token': 'https://api.login.yahoo.com/oauth/v2/get_token',
                'authorize': 'https://api.login.yahoo.com/oauth/v2/request_auth',
                'callback': 'linked_accounts.views.oauth_access_success',
            },
        },

        'facebook': {
            'keys': {
                'KEY': '',
                'SECRET': '',
            },
            'endpoints': {
                'request_token': 'https://graph.facebook.com/oauth/request_token',
                'access_token': 'https://graph.facebook.com/oauth/access_token',
                'authorize': 'https://graph.facebook.com/oauth/authorize',
                'callback': 'linked_accounts.views.oauth_access_success',
                'provider_scope': ['email'],
            },
        },

        'twitter': {
            'keys': {
                'KEY': '',
                'SECRET': '',
            },
            'endpoints': {
                'request_token': 'https://twitter.com/oauth/request_token',
                'access_token': 'https://twitter.com/oauth/access_token',
                'authorize': 'https://twitter.com/oauth/authenticate',
                'callback': 'linked_accounts.views.oauth_access_success',
            },
        },
    }
