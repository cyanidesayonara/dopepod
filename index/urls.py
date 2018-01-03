from django.conf.urls import url
from index import views as index
from podcasts import views as podcasts
from login import views as login

urlpatterns = [
    url(r'^$', index.index, name='index'),
    url(r'^dashboard/$', podcasts.dashboard, name='dashboard'),
    url(r'^search/$', index.search, name='search'),
    url(r'^navbar/$', index.navbar, name='navbar'),
    url(r'^browse/$', index.search, name='browse'),
    url(r'^subscriptions/$', index.subscriptions, name='subscriptions'),
    url(r'^settings/$', index.settings, name='settings'),
    url(r'^charts/$', index.charts, name="charts"),
    url(r'^podinfo/(?P<itunesid>\d+)/$', index.podinfo, name='podinfo'),
    url(r'^episodes/$', podcasts.episodes, name='episodes'),
    url(r'^play/$', podcasts.play, name='play'),
    url(r'^subscribe/$', podcasts.subscribe, name='subscribe'),
    url(r'^login/$', login.login, name='login'),
    url(r'^signup/$', login.signup, name='signup'),
    url(r'^logout/$', login.logout, name='logout'),
    url(r'^password_reset/$', login.password_reset, name='password_reset'),
    url(r"^account/password/reset/key/(?P<uidb36>[0-9A-Za-z]+)-(?P<key>.+)/$", login.password_reset_from_key, name="account_reset_password_from_key"),
]
