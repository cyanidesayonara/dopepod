from django.contrib import admin
from podcasts.models import Podcast, Subscription, Genre, Language, Played_Episode, Playlist_Episode

@admin.register(Podcast)
class PodcastAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'podid', 'rank', 'genre_rank', 'language_rank', 'itunes_rank', 'itunes_genre_rank', 'views', 'plays', 'genre', 'language', 'feedUrl', 'n_subscribers', 'discriminate',)
    fields = ('title', 'artist', 'podid', 'rank', 'genre_rank', 'language_rank', 'itunes_rank', 'itunes_genre_rank', 'views', 'plays', 'genre', 'language', 'feedUrl', 'explicit', 'n_subscribers', 'copyrighttext', 'description', 'reviewsUrl', 'artworkUrl', 'podcastUrl', 'discriminate',)

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'podcast', 'last_updated', 'new_episodes',)
    fields = ('user', 'podcast', 'last_updated', 'new_episodes',)

@admin.register(Played_Episode)
class Played_EpisodeAdmin(admin.ModelAdmin):
    list_display = ('podcast', 'pubDate', 'title', 'description', 'length', 'url', 'kind', 'played_at', 'user',)
    fields = ('podcast', 'pubDate', 'title', 'description', 'length', 'url', 'kind', 'played_at', 'user',)

@admin.register(Playlist_Episode)
class Playlist_EpisodeAdmin(admin.ModelAdmin):
    list_display = ('podcast', 'pubDate', 'title', 'description', 'length', 'url', 'kind', 'added_at', 'user',)
    fields = ('podcast', 'pubDate', 'title', 'description', 'length', 'url', 'kind', 'added_at', 'user',)

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'genreid', 'n_podcasts', 'supergenre',)
    fields = ('name', 'genreid', 'n_podcasts', 'supergenre',)

@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ('name', 'n_podcasts',)
    fields = ('name', 'n_podcasts',)
