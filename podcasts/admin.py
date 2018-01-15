from django.contrib import admin
from podcasts.models import Podcast, Subscription, Chart, Genre, Language

@admin.register(Podcast)
class PodcastAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'podid', 'views', 'genre', 'language', 'genre_rank', 'global_rank', 'feedUrl', 'n_subscribers', 'discriminate')
    fields = ('title', 'artist', 'podid', 'views', 'genre', 'language', 'genre_rank', 'global_rank', 'feedUrl', 'explicit', 'n_subscribers', 'copyrighttext', 'description', 'reviewsUrl', 'artworkUrl', 'podcastUrl', 'discriminate')

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('owner', 'parent', 'last_updated', 'new_episodes')
    fields = ('owner', 'parent', 'last_updated', 'new_episodes',)

@admin.register(Chart)
class ChartAdmin(admin.ModelAdmin):
    list_display = ('header', 'genre',)
    fields = ('podcasts', 'header', 'genre',)

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'genreid', 'n_podcasts', 'supergenre',)
    fields = ('name', 'genreid', 'n_podcasts', 'supergenre',)

@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ('name', 'n_podcasts',)
    fields = ('name', 'n_podcasts',)
