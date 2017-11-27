from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import requests
from lxml import etree

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
        sets self.subscribed = True if subscribed
        """

        if user.is_authenticated:
            subscriptions = Subscription.get_subscriptions_itunesids(user)
            if self.itunesid in subscriptions:
                self.subscribed = True

    def get_tracks(self):
        """
        returns a list of tracks using requests and lxml etree
        """

        ns = {'itunes': 'http://www.itunes.com/dtds/podcast-1.0.dtd',
              'atom': 'http://www.w3.org/2005/Atom',
              'im': 'http://itunes.apple.com/rss',
        }

        tracks = []

        feedUrl = self.feedUrl
        r = requests.get(feedUrl)

        try:
            r.raise_for_status()

            root = etree.XML(r.content)

            ns.update(root.nsmap)
            print(ns)
            tree = root.find('channel')
            podcast = tree.findtext('title')

            for item in tree.findall('item'):
                track = {}
                track['pubDate'] = item.findtext('pubDate')

                # try these
                try:
                    track['title'] = item.findtext('title')
                    track['summary'] = item.findtext('description')
                except AttributeError:
                    # or try with itunes namespace
                    try:
                        track['title'] = item.find('itunes:title', ns).text
                        track['summary'] = item.xpath('itunes:summary', ns).text
                    # if track data not found, skip
                    except AttributeError as e:
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.error('can\'t get track data')
                        continue
                # try to get length
                print(ns['itunes'])
                try:
                    track['length'] = item.find('itunes:duration', ns).text
                except AttributeError as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error('can\'t get length')
                    pass

                track['podcast'] = self

                # link to track
                # enclosure might be missing, have alternatives
                enclosure = item.find('enclosure')
                try:
                    track['url'] = enclosure.get('url')
                    track['type'] = enclosure.get('type')
                    tracks.append(track)
                except AttributeError as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error('can\'t get track url')
            return tracks

        except requests.exceptions.HTTPError as e:
            print(str(e))

    def get_chart(user):
        """
        returns podcast charts
        """

        # charts https://itunes.apple.com/us/rss/toppodcasts/limit=100/gene=1468/language=4/xml
        # reviews https://itunes.apple.com/us/rss/customerreviews/id=xxx/xml

        ns = {'itunes': 'http://www.itunes.com/dtds/podcast-1.0.dtd',
              'atom': 'http://www.w3.org/2005/Atom',
              'im': 'http://itunes.apple.com/rss',
        }

        r = requests.get('https://itunes.apple.com/us/rss/toppodcasts/limit=20/genre=1316/xml')

        try:
            r.raise_for_status()

            root = etree.XML(r.content)

            ns.update(root.nsmap)
            # delete None from namespaces, use atom instead
            del ns[None]

            chart = []
            for entry in root.findall('atom:entry', ns):
                element = entry.find('atom:id', ns)
                itunesid = element.xpath('./@im:id', namespaces=ns)[0]
                try:
                    podcast = Podcast.objects.get(itunesid=itunesid)
                    podcast.is_subscribed(user)
                    chart.append(podcast)
                # TODO if podcast don't exists, scrape it and create it
                except Podcast.DoesNotExist:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error('can\'t get pod')
                    # url = 'https://itunes.apple.com/lookup?id=' + itunesid
                    # json = requests.get(url)
            return chart

        except requests.exceptions.HTTPError as e:
            print(str(e))

class Subscription(models.Model):
    itunesid = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pod = models.ForeignKey('podcasts.Podcast')
    last_updated = models.DateTimeField(default=timezone.now)

    def get_subscriptions(user):
        # make sure not AnonymousUser
        if user.is_authenticated:
            return Subscription.objects.filter(user=user)

    def get_subscriptions_itunesids(user):
        # make sure not AnonymousUser
        if user.is_authenticated:
            return Subscription.objects.filter(user=user).values_list('itunesid', flat=True)

    def update(self):
        self.last_updated = timezone.now()

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

class Genre(Filterable):
    itunesid = models.IntegerField()
    supergenre = models.ForeignKey('podcasts.Genre', blank=True, null=True)

    def get_primary_genres():
        return Genre.objects.filter(supergenre=None).order_by('name')

    # after updating podcast database, count n_podcasts
    def count_n_podcasts():
        genres = Genre.objects.all()
        for genre in genres:
            supergenre = genre.supergenre
            print(Podcast.objects.filter(genre=genre).count())
            genre.n_podcasts = Podcast.objects.filter(genre=genre).count()
            if supergenre == None:
                genre.n_podcasts += Podcast.objects.filter(genre__supergenre=genre).count()
            genre.save()

class Language(Filterable):

    def count_n_podcasts():
        languages = Language.objects.all()
        for language in languages:
            language.n_podcasts = Podcast.objects.filter(language=language).count()
            language.save()
