from haystack import indexes
from .models import Podcast


class PodcastIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.EdgeNgramField(document=True, use_template=True)
    title = indexes.CharField(model_attr='title')
    # for ordering by name
    name = indexes.CharField(model_attr='title', indexed=False)
    artist = indexes.CharField(model_attr='artist')
    initial = indexes.CharField()
    genre = indexes.CharField(model_attr='get_primary_genre')
    language = indexes.CharField(model_attr='language')
    rank = indexes.IntegerField(model_attr='rank', indexed=False, null=True)
    genre_rank = indexes.IntegerField(model_attr='genre_rank', indexed=False, null=True)
    language_rank = indexes.IntegerField(model_attr='language_rank', indexed=False, null=True)
    itunes_rank = indexes.IntegerField(model_attr='itunes_rank', indexed=False, null=True)
    itunes_genre_rank = indexes.IntegerField(model_attr='itunes_genre_rank', indexed=False, null=True)

    def prepare_initial(self, obj):
        words = obj.title.lower().split(" ")
        first = words[0]
        if first == "the" or first == "a" or first == "an":
            try:
                return words[1][0] * 2
            except IndexError:
                pass
        return obj.title[0] * 2

    def prepare_name(self, obj):
        words = obj.title.lower().split(" ")
        first = words[0]
        if first == "the" or first == "a" or first == "an":
            try:
                words = words[1:]
                return " ".join(words)
            except IndexError:
                pass
        return obj.title

    def get_model(self):
        return Podcast

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()
