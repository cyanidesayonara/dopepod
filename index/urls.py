from django.conf.urls import url
from index import views as index
from podcasts import views as podcasts

urlpatterns = [
    url(r'^$', index.index, name='index'),
    url(r'^login/$', index.login, name='login'),
    url(r'^signup/$', index.signup, name='signup'),
    url(r'^reset_password/$', index.reset_password, name='reset_password'),
    url(r'^dashboard/$', podcasts.dashboard, name='dashboard'),
    url(r'^search/$', index.search, name='search'),
    url(r'^navbar/$', index.navbar, name='navbar'),
    url(r'^browse/$', index.browse, name='browse'),
    url(r'^subscriptions/$', index.subscriptions, name='subscriptions'),
    url(r'^settings/$', index.settings, name='settings'),
    url(r'^charts/$', index.charts, name="charts"),
    url(r'^podinfo/(?P<itunesid>\d+)/$', index.podinfo, name='podinfo'),
    url(r'^episodes/$', podcasts.episodes, name='episodes'),
    url(r'^play/$', podcasts.play, name='play'),
    url(r'^subscribe/$', podcasts.subscribe, name='subscribe'),
]
