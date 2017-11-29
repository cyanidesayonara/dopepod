from django.contrib import admin
from podcasts.models import Podcast, Subscription, Chart, Genre, Language

@admin.register(Podcast)
class PodcastAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'chart', 'itunesid', 'genre', 'language', 'feedUrl', 'n_subscribers')
    fields = ('title', 'artist', 'chart', 'itunesid', 'genre', 'language', 'feedUrl', 'explicit', 'n_subscribers', 'copyrighttext', 'description', 'reviewsUrl', 'artworkUrl', 'podcastUrl',)

@admin.register(Subscription)
class SubscriptionAdmin(PodcastAdmin):
    list_display = ('user', 'pod', 'last_updated', 'title', 'artist', 'itunesid', 'genre', 'language', 'feedUrl', 'n_subscribers')
    fields = ('user', 'pod', 'last_updated', 'title', 'artist', 'itunesid', 'genre', 'language', 'feedUrl', 'explicit', 'n_subscribers', 'copyrighttext', 'description', 'reviewsUrl', 'artworkUrl', 'podcastUrl',)

class PodcastInline(admin.TabularInline):
    model = Podcast

@admin.register(Chart)
class ChartAdmin(admin.ModelAdmin):
    list_display = ('genre',)
    fields = ('genre',)
    inlines = [
        PodcastInline,
    ]

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'itunesid', 'n_podcasts', 'supergenre',)
    fields = ('name', 'itunesid', 'n_podcasts', 'supergenre',)

@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ('name', 'n_podcasts',)
    fields = ('name', 'n_podcasts',)

