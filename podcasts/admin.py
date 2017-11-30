from django.contrib import admin
from podcasts.models import Podcast, Subscription, Genre, Language

@admin.register(Podcast)
class PodcastAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'itunesid', 'genre', 'language', 'feedUrl', 'n_subscribers')
    fields = ('title', 'artist', 'itunesid', 'genre', 'language', 'feedUrl', 'explicit', 'n_subscribers', 'copyrighttext', 'description', 'reviewsUrl', 'artworkUrl', 'podcastUrl',)

@admin.register(Subscription)
class SubscriptionAdmin(PodcastAdmin):
    list_display = ('owner', 'parent', 'last_updated', 'title', 'artist', 'itunesid', 'genre', 'language', 'feedUrl', 'n_subscribers')
    fields = ('owner', 'parent', 'last_updated', 'title', 'artist', 'itunesid', 'genre', 'language', 'feedUrl', 'explicit', 'n_subscribers', 'copyrighttext', 'description', 'reviewsUrl', 'artworkUrl', 'podcastUrl',)

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'itunesid', 'n_podcasts', 'supergenre',)
    fields = ('name', 'itunesid', 'n_podcasts', 'supergenre',)

@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ('name', 'n_podcasts',)
    fields = ('name', 'n_podcasts',)

