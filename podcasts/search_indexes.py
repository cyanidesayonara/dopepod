from haystack import indexes
from .models import Podcast


class PodcastIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    title = indexes.CharField(model_attr='title')
    artist = indexes.CharField(model_attr='artist')
    genre = indexes.CharField(model_attr='genre')
    language = indexes.CharField(model_attr='language')

    def get_model(self):
        return Podcast

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()
