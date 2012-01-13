from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('linked_accounts.views',
    url(r'^login/$', 'login', name="linked_accounts_login"),
    url(r'^login/(?P<service>\w+)/$', 'login', name="linked_accounts_service_login"),
    url(r'^complete/(?P<service>\w+)/$', 'auth_complete', name="linked_accounts_complete"),
    url(r'^register/$', 'register', name="linked_accounts_register"),
    url(r'^register/closed/$',
        'registration_closed', name="linked_accounts_registration_closed"),
)
