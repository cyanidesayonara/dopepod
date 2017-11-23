from django.conf.urls import url
from index import views as index
from podcasts import views as podcasts

urlpatterns = [
    url(r'^$', index.search, name='home'),
    url(r'^search/$', index.search, name='search'),
    url(r'^navbar/$', index.navbar, name='navbar'),
    url(r'^browse/$', index.browse, name='browse'),
    url(r'^subscriptions/$', index.subscriptions, name='subscriptions'),
    url(r'^settings/$', index.settings, name='settings'),
    # url(r'^charts/$', podcasts.charts, name="charts"),
    url(r'^podinfo/(?P<itunesid>\d+)/$', podcasts.podinfo, name='podinfo'),
    url(r'^tracks/$', podcasts.tracks, name='tracks'),
    url(r'^play/$', podcasts.play, name='play'),
    url(r'^subscribe/$', podcasts.subscribe, name='subscribe'),
]
