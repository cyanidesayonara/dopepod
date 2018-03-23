from django.conf.urls import url, include
from index import views as index
from podcasts import views as podcasts

urlpatterns = [
    url(r'^$', index.index, name='index'),
    url(r'^dopebar/$', index.dopebar, name='dopebar'),
    url(r'^charts/$', index.charts, name="charts"),
    url(r'^last_played/$', podcasts.last_played, name="last_played"),
    url(r'^search/$', index.search, name='search'),
    url(r'^subscriptions/$', index.subscriptions, name='subscriptions'),
    url(r'^showpod/(?P<podid>\d+)/$', index.showpod, name='showpod'),
    url(r'^episodes/(?P<podid>\d+)/$', podcasts.episodes, name='episodes'),
    url(r'^settings/$', index.settings, name='settings'),
    url(r'^playlist/$', index.playlist, name='playlist'),
    url(r'^subscribe/$', podcasts.subscribe, name='subscribe'),
    url(r'^unsubscribe/$', podcasts.unsubscribe, name='unsubscribe'),
    url(r'^login/$', index.login, name='login'),
    url(r'^signup/$', index.signup, name='signup'),
    url(r'^logout/$', index.logout, name='logout'),
    url(r'^password_reset/$', index.password_reset, name='password_reset'),
    url(r"^account/password/reset/key/(?P<uidb36>[0-9A-Za-z]+)-(?P<key>.+)/$", index.password_reset_from_key, name="account_reset_password_from_key"),
]
