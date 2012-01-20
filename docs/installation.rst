============
Installation
============

Installing and integrating Django Linked Accounts requires the
following steps:

#. `Install Dependencies`_
#. `Install Django App`_
#. `Include URLs`_
#. `Add Authentication Backend`_
#. `Obtain Service Keys`_
#. `Add Settings`_

.. _install-dependencies:

Install Dependencies
--------------------

Django Linked Accounts depends on `django-oauth-flow
<https://github.com/zen4ever/django-oauth-flow>`_.

You can run the following commands through ``pip install`` to install
the necessary dependencies:

::

    -e git://github.com/zen4ever/django-oauth-flow.git#egg=django-oauth-flow
    httplib2>=0.6.0
    oauth2>=1.5.167

Or use supplied ``requirements.txt`` file:

::

    git clone git://github.com/zen4ever/django-linked-accounts.git
    cd django-linked-accounts/
    pip install -r requirements.txt

You can install the python package with the following:

::

    pip install -e git://github.com/zen4ever/django-linked-accounts.git

.. _install-django-app:

Install Django App
------------------

Add ``linked_accounts`` to your ``INSTALLED_APPS``
(``settings.py``):

.. code-block:: python

    INSTALLED_APPS = (
        # ...
        "linked_accounts",
    )

.. _install-urls:

Include URLs
------------

Include URLs for ``linked_accounts`` in your URLconf (``urls.py``):

.. code-block:: python

    urlpatterns = patterns("",
        # ...
        url(r"^linked_accounts/", include("linked_accounts.urls"))
    )

.. _add-authentication-backend:

Add Authentication Backend
--------------------------

Add the custom authentication backend to your
``AUTHENTICATION_BACKENDS`` (``settings.py``) to allow OAuth authentication
with Django Linked Accounts.

.. code-block:: python

    AUTHENTICATION_BACKENDS = (
        'django.contrib.auth.backends.ModelBackend',
        'linked_accounts.backends.LinkedAccountsBackend',
    )

.. _obtain-service-keys:

Obtain Service Keys
-------------------

You will need to obtain a ``KEY`` and ``SECRET`` with each third-party
service you want to support. Yes, it's tedious. But, hey, you only have
to do it once for your app and you can piggyback on established social
graphs and make things easier for your users by importing information
already entered elsewhere.

Here are some handy reference links to get you started:

- Facebook: `https://developers.facebook.com/apps <hhttps://developers.facebook.com/apps>`_ (click the "Create New App" button...)
- Twitter: `https://dev.twitter.com/apps/new <https://dev.twitter.com/apps/new>`_
- Google: `https://code.google.com/apis/console/ <https://code.google.com/apis/console/>`_
- Yahoo: `https://developer.apps.yahoo.com/wsregapp <https://developer.apps.yahoo.com/wsregapp/>`_
- LinkedIn: `https://www.linkedin.com/secure/developer <https://www.linkedin.com/secure/developer>`_

Most of these services require you to register an authentication
callback URL to redirect to after a user authorizes your app.
Here's an example callback URL for Twitter:

.. code-block:: html

  http://yourdomain.com/linked_accounts/complete/twitter/

.. _add-settings:

Add Settings
------------

Lastly, add OAuth settings in your ``settings.py`` for each service
you want to integrate with using the ``KEY`` and ``SECRET`` values
you obtained in the previous installation step.

Use the following code as a reference and include only the services
you want to support:

.. code-block:: python

    OAUTH_FLOW_SETTINGS = {
        'facebook': {
            'KEY': '',
            'SECRET': '',
            'SCOPE': ['email'],
        },
        'twitter': {
            'KEY': '',
            'SECRET': '',
        },
        'google': {
            'KEY': '',
            'SECRET': '',
            'SCOPE': ['https://www.googleapis.com/auth/userinfo.profile']
        },
        'yahoo': {
            'KEY': '',
            'SECRET': '',
        }
    }
