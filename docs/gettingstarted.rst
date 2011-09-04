===============
Getting Started
===============

Welcome to the documentation for Django Linked Accounts. Here you'll
find everything you need to get started using this reusable app in
your Django projects. Good luck and thanks for reading!

Settings
========

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

This setting is used in a session variable that stores the desired URL
to be redirected to following successful OAuth login. Make sure to
create the corresponding view if you set a custom value here.

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
          ('linkedin', 'linked_accounts.handlers.LinkedInHandler'),
      )

This setting contains a set of classes responsible for retrieving user
profile information for third-party services. It is inherited from
``AuthHandler``, but can be overridden by supplying your own classes.

.. _linked_accounts_always_update_profile:

``LINKED_ACCOUNTS_ALWAYS_UPDATE_PROFILE``
------------------------------

Default: ``False``

Set this to ``True`` if you want the data stored in
``LinkedAccount.api_response`` each time a user successfully logs in
via OAuth. Keep the default value to only update this data once
during the first OAuth login for each service.

Login
=====

Django Linked Accounts contains a sample login view. It displays the
template "linked_accounts/login.html", which should contain a list of
links/buttons login with the individual services you , for example:

.. code-block:: html

  <a href="{% url oauth_access_login "facebook" %}">Sign in with Facebook</a>
  <a href="{% url oauth_access_login "twitter" %}">Sign in with Twitter</a>

It also saves next url passed as a GET parameter "next" in a session variable,
so user will be redirected to it upon successful authentication. If you are
going to use Django Linked Accounts as your main authentication mechanism,
you can just specify in your settings.py:

.. code-block:: python

   LOGIN_URL = "/linked_accounts/login/"

Alternatively you can pass additional "service" parameter to the login view,
then it will skip template rendering and redirect you to the oauth login view,
preserving "next" url in the variable. If you are planning to use Django Linked
Accounts as a supplemental app to ``django.contrib.auth``, you can place a set
of links in your "accounts/login.html" somewhere above or below your main login
form, like this:

.. code-block:: html

  <a href="{% url linked_accounts_login %}?service=facebook&amp;next={{ next }}">Sign in with Facebook</a>
  <a href="{% url linked_accounts_login %}?service=twitter&amp;next={{ next }}">Sign in with Twitter</a>

Registration
============

Registration happens when OAuth authorization with a service is completed, new
``LinkedAccount`` profile gets created, and current user is not authenticated
yet. So, user will be redirected to "/linked_accounts/register/", where they can
choose a username and specify their email (if service provides user's email
during OAuth authentication, it will be listed as an initial value in the
registration form).

Once form is submitted, new ``User`` is created and will be automatically
logged in.

You can disallow registration process by setting
``LINKED_ACCOUNTS_ALLOW_REGISTRATION`` to False in your settings.py.
It will prevent creation of new users authenticated with third-party services
(might be useful for private betas, or closed websites). Currently active users
with already associated third-party service profiles still will be able to
login.

Django Linked Accounts provides a simple ``RegistrationForm`` which is
used to collect each user's email address during registration. However,
please note that the app does not handle email confirmation or any other
transactional email notifications. If this app does not match the desired
flow for your project, you can override the registration form, view, or
even individual methods found in ``AuthCallback``.
