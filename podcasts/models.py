from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class PodcastBase(models.Model):
    itunesid = models.IntegerField(primary_key=True)
    feedUrl = models.URLField(max_length=500)
    title = models.CharField(max_length=255)
    genre = models.ForeignKey('podcasts.Genre')
    explicit = models.BooleanField()
    language = models.ForeignKey('podcasts.Language', null=True, blank=True)
    copyrighttext = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    reviewsUrl = models.URLField(max_length=255)
    artworkUrl = models.URLField(max_length=255)
    podcastUrl = models.URLField(max_length=255)

    class Meta:
        abstract = True

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('podinfo', args='self.itunesid')

class Podcast(PodcastBase):
    n_subscribers = models.IntegerField()
    subscribed = models.BooleanField(default=False)

class PodcastSubscription(PodcastBase):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    itunesid = models.IntegerField()
    last_updated = models.DateTimeField(default=timezone.now)

    def update(self):
        print(timezone.now)
        last_updated = timezone.now

class Filterable(models.Model):
    name = models.CharField(primary_key=True, max_length=50)
    n_podcasts = models.IntegerField()

    class Meta:
        abstract = True

    def __str__(self):
        return self.name

    # after updating podcast database, count n_podcasts for each filterable
    def count_n_podcasts(self):
        objs = self.objects.all()
        for obj in objs:
            # if obj has attr supa, it's a Genre
            try:
                supa = obj.supa
                obj.n_podcasts = Podcast.objects.filter(genre=obj).count()
                if supa == None:
                    obj.n_podcasts += Podcast.objects.filter(genre__supa=obj).count()
            # if obj doesn't have attr supa, it's a Language
            except AttributeError:
                obj.n_podcasts = Podcast.objects.filter(language=obj.name).count()    
            obj.save()

class Genre(Filterable):
    supa = models.ForeignKey('podcasts.Genre', blank=True, null=True)

    def get_primary_genres(self):
        return self.objects.filter(supa=None).order_by('name')

class Language(Filterable):
    pass
