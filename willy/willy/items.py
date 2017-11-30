# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html
import scrapy
from scrapy_djangoitem import DjangoItem
from podcasts.models import Podcast, Genre


class PodcastItem(DjangoItem):
    django_model = Podcast

class GenreItem(DjangoItem):
    django_model = Genre
