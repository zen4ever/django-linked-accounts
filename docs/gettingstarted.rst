===============
Getting Started
===============

Welcome to the documentation for Django Linked Accounts. Here you'll
find everything you need to get started using this reusable app in
your Django projects. Good luck and thanks for reading!

Settings
========

The following are optional settings variables that can be included in
your project's ``settings.py`` to override certain defaults.

.. _linked_accounts_allow_registration:

``LINKED_ACCOUNTS_ALLOW_REGISTRATION``
--------------------------------------

Default: ``True``

Set this to ``False`` to prohibit auth.User creation after OAuth login.
This is useful if you want to only allow your users to link third-party
accounts to their existing auth.User account, but not allow sign up via
third-party service.

.. _linked_accounts_allow_login:

``LINKED_ACCOUNTS_ALLOW_LOGIN``
-------------------------------

Default: ``True``

Set this to ``False`` to prohibit users from logging in via OAuth.
This is useful if you want to only retrieve data from a third-party
service that requires OAuth authentication.

.. _linked_accounts_next_key:

``LINKED_ACCOUNTS_NEXT_KEY``
----------------------------

Default: ``oauth_next``

This setting can be used to override the default session variable
key used to store ``next_url`` between redirects to and from OAuth services.
You probably won't need to change this setting unless you use the
``oauth_next`` session key for something else in your project.

.. _linked_accounts_id_session:

``LINKED_ACCOUNTS_ID_SESSION``
------------------------------

Default: ``_linked_account_id``

Modify this setting to change the session key that stores the
``LinkedAccount`` id temporarily during sign up via third-party
service.

.. _linked_accounts_handlers:

``LINKED_ACCOUNTS_HANDLERS``
----------------------------

Default:
  .. code-block:: python

      LINKED_ACCOUNTS_HANDLERS = (
          ('facebook', 'linked_accounts.handlers.FacebookHandler'),
          ('twitter', 'linked_accounts.handlers.TwitterHandler'),
          ('google', 'linked_accounts.handlers.GoogleHandler'),
          ('yahoo', 'linked_accounts.handlers.YahooHandler'),
      )

This setting contains a set of classes responsible for retrieving user
profile information for third-party services. It is inherited from
``AuthHandler``, but can be overridden by supplying your own classes.

.. _linked_accounts_always_update_profile:

``LINKED_ACCOUNTS_ALWAYS_UPDATE_PROFILE``
-----------------------------------------

Default: ``False``

Set this to ``True`` if you want the data stored in
``LinkedAccount.api_response`` each time a user successfully logs in
via OAuth. Keep the default value to only update this data once
during the first OAuth login for each service.

``LINKED_ACCOUNTS_EMAIL_MATCH``
-------------------------------

Default: ``True``

Will attempt to look for LinkedAccount on login assuming that email is an
identifier. Useful when you migrating your authentication system from OpenID,
because your OpenID identifier will never match your OAuth identifier.

``LINKED_ACCOUNTS_AUTO_REGISTRATION``
-------------------------------

Default: ``True``

Instead of redirecting to registration form will automatically create a new
user with suitable username.


Login
=====

Django Linked Accounts contains a sample login view.

It displays the template "linked_accounts/login.html", which contains
login links for each supported service. For example:

.. code-block:: html

  <a href="{% url linked_accounts_service_login "facebook" %}">Sign in with Facebook</a>
  <a href="{% url linked_accounts_service_login "twitter" %}">Sign in with Twitter</a>

The login view also saves the GET parameter ``next`` in a session variable
that is used to redirect the user after successful OAuth authentication.

If you are going to use Django Linked Accounts as your main authentication
mechanism, set the following in your ``settings.py``:

.. code-block:: python

   LOGIN_URL = "/linked_accounts/login/"

Alternatively, you can pass the additional GET parameter ``service`` to
the login view to bypass Django Linked Accounts' login template rendering
and redirect you to the django-oauth-access login view, preserving ``next``
GET parameter in the redirect URL.

If you are planning to use Django Linked Accounts as a supplemental app to
``django.contrib.auth``, for example, to link existing third-party accounts
to ``auth.User`` accounts, you can include links in your
``linked_accounts/login.html`` in addition to your ``auth.User`` login form
like this:

.. code-block:: html

  <a href="{% url linked_accounts_login %}?service=facebook&amp;next={{ next }}">Sign in with Facebook</a>
  <a href="{% url linked_accounts_login %}?service=twitter&amp;next={{ next }}">Sign in with Twitter</a>

Registration
============

Django Linked Accounts contains a simple registration view.

When a logged-out user successfully completes OAuth authentication with a
third-party service, a new ``LinkedAccount`` profile is created and the
user is redirected to ``/linked_accounts/register/`` where they can choose
a username and enter their email address. If an email address was collected
during OAuth authentication, it will be listed as an initial value in the
registration form.

Once the registration form is submitted, a new ``auth.User`` is created and
is logged in.

You can prohibit registration via third-party services by setting
``LINKED_ACCOUNTS_ALLOW_REGISTRATION`` to ``False`` in your ``settings.py``.
This will prevent the creation of new users authenticated with third-party
services, which might be useful for private betas or similar. Please note that
if a valid ``auth.User`` is already linked to a third-party service in Django
Linked Accounts, login via that service will be allowed.

Django Linked Accounts provides a simple ``RegistrationForm`` which is
used to collect each user's email address during registration. However,
please note that this app does not handle email confirmation or any other
transactional email notifications. If this app does not match the desired
flow for your project, you can inherit and override the registration form,
view, or even individual methods found in ``AuthCallback`` in your own custom
views.
