from django.contrib import admin
from podcasts.models import Podcast, Subscription, Chart, Genre, Language, Episode, Order

@admin.register(Podcast)
class PodcastAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'podid', 'rank', 'views', 'genre', 'language', 'feedUrl', 'n_subscribers', 'discriminate', 'last_episode')
    fields = ('title', 'artist', 'podid', 'rank', 'views', 'genre', 'language', 'feedUrl', 'explicit', 'n_subscribers', 'copyrighttext', 'description', 'reviewsUrl', 'artworkUrl', 'podcastUrl', 'discriminate', 'last_episode')

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'podcast', 'last_updated', 'new_episodes')
    fields = ('user', 'podcast', 'last_updated', 'new_episodes',)

@admin.register(Chart)
class ChartAdmin(admin.ModelAdmin):
    list_display = ('header', 'provider', 'genre',)
    fields = ('header', 'provider', 'genre',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('position', 'podcast', 'chart',)
    fields = ('position', 'podcast', 'chart',)

@admin.register(Episode)
class EpisodeAdmin(admin.ModelAdmin):
    list_display = ('parent', 'pubDate', 'title', 'summary', 'length', 'url', 'kind', 'played')
    fields = ('parent', 'pubDate', 'title', 'summary', 'length', 'url', 'kind', 'played')

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'genreid', 'n_podcasts', 'supergenre',)
    fields = ('name', 'genreid', 'n_podcasts', 'supergenre',)

@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ('name', 'n_podcasts',)
    fields = ('name', 'n_podcasts',)
