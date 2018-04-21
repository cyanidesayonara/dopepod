from django.conf.urls import url
from index import views as index
from podcasts import views as podcasts

urlpatterns = [
    url(r"^$", index.index, name="index"),
    url(r"^dopebar/$", index.dopebar, name="dopebar"),
    url(r"^charts/$", index.charts, name="charts"),
    url(r"^last-played/$", podcasts.last_played, name="last_played"),
    url(r"^search/$", index.search, name="search"),
    url(r"^subscriptions/$", index.subscriptions, name="subscriptions"),
    url(r"^showpod/(?P<podid>\d+)/$", index.showpod, name="showpod"),
    url(r"^episodes/(?P<podid>\d+)/$", podcasts.episodes, name="episodes"),
    url(r"^settings/$", index.settings, name="settings"),
    url(r"^playlist/$", index.playlist, name="playlist"),
    url(r"^login/$", index.login, name="login"),
    url(r"^signup/$", index.signup, name="signup"),
    url(r"^logout/$", index.logout, name="logout"),
    url(r"^change-password/$", index.change_password, name="change_password"),
    url(r"^password-reset/$", index.password_reset, name="password_reset"),
    url(r"^account/password/reset/key/(?P<uidb36>[0-9A-Za-z]+)-(?P<key>.+)/$", index.password_reset_from_key, name="password_reset_from_key"),
    url(r"^account/confirm-email/(?P<key>[-:\w]+)/$", index.confirm_email, name="confirm_email"),
    url(r"^noshow/$", index.noshow, name="noshow"),
    url(r"^solong/$", index.solong, name="solong"),
]
