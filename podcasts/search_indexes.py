from haystack import indexes
from .models import Podcast


class PodcastIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.EdgeNgramField(document=True, use_template=True)
    title = indexes.CharField(model_attr='title')
    initial = indexes.CharField()
    artist = indexes.CharField(model_attr='artist')
    genre = indexes.CharField(model_attr='get_primary_genre')
    language = indexes.CharField(model_attr='language')
    rank = indexes.IntegerField(model_attr='rank', indexed=False, null=True)
    genre_rank = indexes.IntegerField(model_attr='genre_rank', indexed=False, null=True)
    language_rank = indexes.IntegerField(model_attr='language_rank', indexed=False, null=True)
    itunes_rank = indexes.IntegerField(model_attr='itunes_rank', indexed=False, null=True)
    itunes_genre_rank = indexes.IntegerField(model_attr='itunes_genre_rank', indexed=False, null=True)

    def prepare_initial(self, obj):
        if obj.title.split(" ")[0].capitalize() == "The":
            return obj.title.split(" ")[1][0].lower()
        else:
            return obj.title[0].lower()

    def get_model(self):
        return Podcast

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()
