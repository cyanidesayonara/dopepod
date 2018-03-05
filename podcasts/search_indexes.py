from haystack import indexes

from .models import Podcast

class PodcastIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    title = indexes.CharField(model_attr='title')
    artist = indexes.CharField(model_attr='artist')

    def get_model(self):
        return Podcast

    def index_queryset(self, using=None):
        return self.get_model().objects.all()
