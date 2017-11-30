# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from willy.items import GenreItem, PodcastItem
from podcasts.models import Genre, Podcast, Filterable

class WillyPipeline(object):
    def __init__(self):
        self.ids_seen = set()

    def process_item(self, item, spider):
        if type(item) is PodcastItem:
            itunesid = item['itunesid']
            if itunesid not in self.ids_seen:
                Podcast.create_or_update_podcast(item)
                self.ids_seen.add(itunesid)
        elif type(item) is GenreItem:
            Genre.create_or_update_genre(item)

    def close_spider(self, spider):
        Filterable.count_n_podcasts()
