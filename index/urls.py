from django.conf.urls import url
from index import views

urlpatterns = [
    # url(r'^x$', views.ajax_home, name='ajax_home'),
    url(r'^$', views.home, name='home'),
    url(r'^navbar/$', views.navbar, name='navbar'),
    url(r'^browse/$', views.browse, name='browse'),
    url(r'^subscriptions/$', views.subscriptions, name='subscriptions'),
    url(r'^settings/$', views.settings, name='settings'),
]
