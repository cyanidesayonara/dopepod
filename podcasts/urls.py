from django.conf.urls import url, include
from podcasts import views

urlpatterns = [
    url(r'^charts/$', views.charts, name="charts"),
    url(r'^search/$', views.search, name='search'),
    # url(r'^search/?P<q>\w+/$', views.q_search, name='q_search'),
    url(r'^podinfo/$', views.ajax_podinfo, name='ajax_podinfo'),
    url(r'^podinfo/(?P<itunesid>\w+)/$', views.podinfo, name='podinfo'),
    url(r'^tracks/$', views.tracks, name='tracks'),
    url(r'^play/$', views.play, name='play'),
    url(r'^subscribe/$', views.subscribe, name='subscribe'),
]
