from django import forms
from podcasts.models import Podcast

class PodcastForm(forms.ModelForm):

    class Meta:
        model = Podcast
        fields = ('collectionName', 'genre')
