from django.conf.urls import url, include
from podcasts import views

urlpatterns = [
    url(r'^charts/$', views.charts, name="charts"),
    url(r'^search/$', views.search, name='search'),
    url(r'^podinfo/(?P<itunesid>\w+)/$', views.podinfo_ext, name='podinfo_ext'),
    url(r'^podinfo/(?P<itunesid>\w+)/i$', views.podinfo, name='podinfo'),
    url(r'^tracks/$', views.tracks, name='tracks'),
    url(r'^play/$', views.play, name='play'),
    url(r'^subscriptions/$', views.subscriptions_ext, name='subscriptions_ext'),
    url(r'^subscriptions/i$', views.subscriptions, name='subscriptions'),
    url(r'^subscribe/$', views.subscribe, name='subscribe'),
]
