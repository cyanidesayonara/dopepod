from django.conf.urls import url
from django.contrib.auth import views as auth_views
from django.contrib.sites.models import Site
from index import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^navbar/$', views.navbar, name='navbar'),
    url(r'^subscriptions/i$', views.ajax_subscriptions, name='ajax_subscriptions'),
    url(r'^subscriptions/$', views.subscriptions, name='subscriptions'),
    url(r'^profile/$', views.edit_profile, name='edit_profile'),
    url(r'^profile/(?P<username>\w+)/$', views.profile, name='profile'),
]
