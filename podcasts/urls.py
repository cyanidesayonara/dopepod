from django.conf.urls import url
from podcasts import views

urlpatterns = [
    # url(r'^charts/$', views.charts, name="charts"),
    url(r'^search/$', views.search, name='search'),
    url(r'^podinfo/(?P<itunesid>\d+)/$', views.podinfo, name='podinfo'),
    url(r'^tracks/$', views.tracks, name='tracks'),
    url(r'^play/$', views.play, name='play'),
    url(r'^play/(?P<url>.+)/$', views.play, name='play'),
    url(r'^subscribe/$', views.subscribe, name='subscribe'),
]
