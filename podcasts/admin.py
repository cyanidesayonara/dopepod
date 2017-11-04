from django.contrib import admin
from podcasts.models import Podcast, Subscription, Genre, Language

@admin.register(Podcast)
class PodcastAdmin(admin.ModelAdmin):
    list_display = ('title', 'itunesid', 'genre', 'language', 'feedUrl', 'n_subscribers')
    fields = ('title', 'itunesid', 'genre', 'language', 'feedUrl', 'explicit', 'n_subscribers', 'copyrighttext', 'description', 'reviewsUrl', 'artworkUrl', 'podcastUrl',)

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('itunesid', 'user', 'pod', 'last_updated',)
    fields = ('itunesid', 'user', 'pod', 'last_updated',)

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'n_podcasts', 'supergenre',)
    fields = ('name', 'n_podcasts', 'supergenre',)

@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ('name', 'n_podcasts',)
    fields = ('name', 'n_podcasts',)

