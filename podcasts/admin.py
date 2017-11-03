from django.contrib import admin
from podcasts.models import Podcast, PodcastSubscription, Genre, Language

@admin.register(Podcast)
class PodcastAdmin(admin.ModelAdmin):
    list_display = ('title', 'itunesid', 'genre', 'language', 'feedUrl', 'n_subscribers')
    fields = ('title', 'itunesid', 'genre', 'language', 'feedUrl', 'explicit', 'n_subscribers', 'copyrighttext', 'description', 'reviewsUrl', 'artworkUrl', 'podcastUrl',)

@admin.register(PodcastSubscription)
class PodcastSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'last_updated', 'itunesid', 'genre', 'language', 'feedUrl',)
    fields = ('title', 'user', 'last_updated', 'itunesid', 'genre', 'language', 'feedUrl', 'explicit', 'copyrighttext', 'description', 'reviewsUrl', 'artworkUrl', 'podcastUrl',)

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'n_podcasts', 'supa',)
    fields = ('name', 'n_podcasts', 'supa',)

@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ('name', 'n_podcasts',)
    fields = ('name', 'n_podcasts',)

