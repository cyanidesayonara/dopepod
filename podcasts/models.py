from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import requests
import xml.etree.ElementTree as ET

class Podcast(models.Model):
    itunesid = models.IntegerField(primary_key=True)
    feedUrl = models.URLField(max_length=500)
    title = models.CharField(max_length=255)
    genre = models.ForeignKey('podcasts.Genre')
    explicit = models.BooleanField()
    language = models.ForeignKey('podcasts.Language', null=True, blank=True)
    copyrighttext = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    n_subscribers = models.IntegerField()
    subscribed = models.BooleanField(default=False)
    reviewsUrl = models.URLField(max_length=255)
    artworkUrl = models.URLField(max_length=255)
    podcastUrl = models.URLField(max_length=255)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('podinfo', args='self.itunesid')

    def is_subscribed(self, user):
        """
        get a list of itunesids from user's subscriptions
        (if not AnonymousUser),
        if self.itunesid on list, self.subscribed = True
        """
        if user.username:
            subscriptions = Subscription.get_subscriptions_itunesids(user)
            if self.itunesid in subscriptions:
                self.subscribed = True

    def get_tracks(self):
        """
        returns a list of tracks using requests and ElementTree
        """

        ns = {'itunes': 'http://www.itunes.com/dtds/podcast-1.0-dtd',
              'atom': 'http://www.w3.org/2005/Atom'}

        tracks = []

        # TODO fix this shit
        feedUrl = self.feedUrl
        r = requests.get(feedUrl)
        root = ET.fromstring(r.text)
        tree = root.find('channel')
        podcast = tree.find('title').text

        for item in tree.findall('item'):
            track = {}
            track['podcast'] = podcast
            track['pubDate'] = item.find('pubDate').text

            # try these
            try:
                track['title'] = item.find('title').text
                track['summary'] = item.find('description').text
            except AttributeError:
                # or try with itunes namespace
                try:
                    track['title'] = item.find('itunes:title', ns).text
                    track['summary'] = item.find('itunes:summary', ns).text
                # if track data not found, skip
                except AttributeError as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error('can\'t get track data')
                    continue
            # try to get length (EXPERIMENTAL)S
            try:
                track['length'] = item.find('itunes:duration', ns).text
            except AttributeError as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error('can\'t get length')

            # link to track
            # enclosure might be missing, have alternatives
            enclosure = item.find('enclosure')
            track['url'] = enclosure.get('url')
            track['type'] = enclosure.get('type')
            tracks.append(track)
        return tracks

class Subscription(models.Model):
    itunesid = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pod = models.ForeignKey('podcasts.Podcast')
    last_updated = models.DateTimeField(default=timezone.now)

    def get_subscriptions(user):
        # make sure not AnonymousUser
        if user.username:
            return Subscription.objects.filter(user=user)
        else:
            return None

    def get_subscriptions_itunesids(user):
        # make sure not AnonymousUser
        if user.username:
            return Subscription.objects.filter(user=user).values_list('itunesid', flat=True)
        else:
            return None

    def update(self):
        last_updated = timezone.now

class Filterable(models.Model):
    """
    meta class for genre and language
    """

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
    supergenre = models.ForeignKey('podcasts.Genre', blank=True, null=True)

    def get_primary_genres(self):
        return self.objects.filter(supergenre=None).order_by('name')

class Language(Filterable):
    pass
