# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from podcasts.models import Podcast, Filterable

class WillyPipeline(object):

    def close_spider(self, spider):
        """
        counts n_podcasts for all genres and languages
        """

        Filterable.count_n_podcasts()
