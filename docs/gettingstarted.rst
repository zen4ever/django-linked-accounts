===============
Getting Started
===============

Login
=====

Django Linked Accounts contains login view. It displays template
"linked_accounts/login.html" which should contain a list of links
to start login with individual services, for example:

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

Email confirmation
==================

By default Django Linked Accounts provides very simple ``RegistrationForm``
which only asks users for their email, but doesn't actually do any email
confirmation steps. Depending on your flow you might want to supply your own
registration form. For example, you could use django-emailconfirmation to send a
confirmation email to user.

Settings
========

 * ``LINKED_ACCOUNTS_ALLOW_REGISTRATION`` - set to False if you don't want to
   allow new user creation after OAuth login

 * ``LINKED_ACCOUNTS_ALLOW_LOGIN`` - set to False if you don't want to allow users
   to login with OAuth. (Useful, if you just want to use Linked Accounts to
   retrieve user's profile for certain service, and store it, but still want
   your users to login just using username/password.

 * ``LINKED_ACCOUNTS_NEXT_KEY`` - session key for storing next url during user
   login, defaults to "oauth_next"

 * ``LINKED_ACCOUNTS_ID_SESSION`` - session key for storing ``LinkedAccount`` id after
   initial profile creation, but before registration, defaults to
   '_linked_account_id'

 * ``LINKED_ACCOUNTS_HANDLERS`` - set of classes responsible for retrieving user
   profile information for third-party services, inherited from ``AuthHandler``,
   you can override them by supplying your own class. Default value:

   .. code-block:: python

      LINKED_ACCOUNTS_HANDLERS = (
          ('facebook', 'linked_accounts.handlers.FacebookHandler'),
          ('twitter', 'linked_accounts.handlers.TwitterHandler'),
          ('google', 'linked_accounts.handlers.GoogleHandler'),
          ('yahoo', 'linked_accounts.handlers.YahooHandler'),
          ('linkedin', 'linked_accounts.handlers.LinkedInHandler'),
      )

 * ``LINKED_ACCOUNTS_ALWAYS_UPDATE_PROFILE`` - set to True if you want to update
   third-party service's profile information stored in
   ``LinkedAccount.api_response`` each time user performes OAuth login into
   the service. By default it will fetch profile data only during account
   creation, and store it as a JSON.
