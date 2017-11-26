# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from willy.items import GenreItem, PodcastItem, LanguageItem
from podcasts.models import Genre, Podcast, Language

class WillyPipeline(object):
    def __init__(self):
        self.ids_seen = set()

    def process_item(self, item, spider):
        if type(item) is PodcastItem:
            itunesid = item['itunesid']
            if itunesid not in self.ids_seen:
                create_or_update_podcast(item)
                self.ids_seen.add(itunesid)
        elif type(item) is GenreItem:
            create_genre(item)

    def close_spider(self, spider):
        Genre.count_n_podcasts()
        Language.count_n_podcasts()

def create_genre(item):
    supergenre = None
    if item['supergenre']:
        supergenre = Genre.objects.get(name=item['supergenre'])
    try:
        genre = Genre.objects.get(name=item['name'])
        genre.n_podcasts = 0
        genre.supergenre = supergenre
        genre.save()
    except Genre.DoesNotExist:
        Genre.objects.create(
                    name=item['name'],
                    itunesid=item['itunesid'],
                    n_podcasts=0,
                    supergenre=supergenre
                    )

def create_or_update_podcast(item):
    genre = Genre.objects.get(name=item['genre'])
    if item['language']:
        language = create_or_get_language(item['language'])
        try:
            podcast = Podcast.objects.get(itunesid=item['itunesid'])
            podcast.feedUrl = item['feedUrl']
            podcast.title = item['title']
            podcast.genre = genre
            podcast.explicit = item['explicit']
            podcast.language = language
            podcast.copyrighttext = item['copyrighttext']
            podcast.description = item['description']
            podcast.reviewsUrl = item['reviewsUrl']
            podcast.artworkUrl = item['artworkUrl']
            podcast.podcastUrl = item['podcastUrl']
            podcast.save()
        except Podcast.DoesNotExist:
            Podcast.objects.create(
                itunesid=item['itunesid'],
                feedUrl=item['feedUrl'],
                title=item['title'],
                genre=genre,
                n_subscribers=0,
                explicit=item['explicit'],
                language=language,
                copyrighttext=item['copyrighttext'],
                description=item['description'],
                reviewsUrl=item['reviewsUrl'],
                artworkUrl=item['artworkUrl'],
                podcastUrl=item['podcastUrl'],
            )

def create_or_get_language(name):
    try:
        language = Language.objects.get(name=name)
    except Language.DoesNotExist:
        language = Language.objects.create(
                    name=name,
                    n_podcasts=0,
                    )
    return language
