from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('linked_accounts.views',
    url(r'^login/$', 'login', name="linked_accounts_login"),
    url(r'^register/$', 'register', name="linked_accounts_register"),
)
