from django import forms
from .models import Podcast, Episode

class PodcastForm(forms.ModelForm):

    class Meta:
        model = Podcast
        exclude = ('genre_rank', 'global_rank', 'subscribed', 'n_subscribers')

class EpisodeForm(forms.ModelForm):

    class Meta:
        model = Episode
        fields = ('parent', 'pubDate', 'summary', 'length', 'url', 'kind')