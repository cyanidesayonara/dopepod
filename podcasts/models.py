from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import requests
from lxml import etree, html

class Podcast(models.Model):
    itunesid = models.IntegerField(primary_key=True)
    feedUrl = models.URLField(max_length=500)
    title = models.CharField(max_length=255)
    artist = models.CharField(max_length=255)
    genre = models.ForeignKey('podcasts.Genre')
    explicit = models.BooleanField()
    language = models.ForeignKey('podcasts.Language')
    copyrighttext = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    n_subscribers = models.IntegerField()
    subscribed = models.BooleanField(default=False)
    reviewsUrl = models.URLField(max_length=255)
    artworkUrl = models.URLField(max_length=255)
    podcastUrl = models.URLField(max_length=255)

    def create_or_update_podcast(item):
        genre = Genre.objects.get(name=item['genre'])
        language = Language.create_or_get_language(item['language'])
        try:
            podcast = Podcast.objects.get(itunesid=item['itunesid'])
            podcast.feedUrl = item['feedUrl']
            podcast.title = item['title']
            podcast.artist = item['artist']
            podcast.genre = genre
            podcast.explicit = item['explicit']
            podcast.language = language
            podcast.copyrighttext = item['copyrighttext']
            podcast.description = item['description']
            podcast.reviewsUrl = item['reviewsUrl']
            podcast.artworkUrl = item['artworkUrl']
            podcast.podcastUrl = item['podcastUrl']
            podcast.save()
        except Podcast.DoesNotExist:
            Podcast.objects.create(
                itunesid=item['itunesid'],
                feedUrl=item['feedUrl'],
                title=item['title'],
                artist=item['artist'],
                genre=genre,
                n_subscribers=0,
                explicit=item['explicit'],
                language=language,
                copyrighttext=item['copyrighttext'],
                description=item['description'],
                reviewsUrl=item['reviewsUrl'],
                artworkUrl=item['artworkUrl'],
                podcastUrl=item['podcastUrl'],
            )

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('podinfo', args='self.itunesid')

    def is_subscribed(self, user):
        """
        sets self.subscribed = True if subscribed
        """

        subscriptions = Subscription.get_subscriptions_itunesids(user)
        if subscriptions:
            if self.itunesid in subscriptions:
                self.subscribed = True

    def get_episodes(self):
        """
        returns a list of episodes using requests and lxml etree
        """

        ns = {'itunes': 'http://www.itunes.com/dtds/podcast-1.0.dtd',
              'atom': 'http://www.w3.org/2005/Atom',
              'im': 'http://itunes.apple.com/rss',
        }

        episodes = []

        feedUrl = self.feedUrl
        r = requests.get(feedUrl, timeout=1)

        try:
            r.raise_for_status()

            root = etree.XML(r.content)

            ns.update(root.nsmap)
            tree = root.find('channel')
            podcast = tree.findtext('title')

            for item in tree.findall('item'):
                episode = {}
                episode['pubDate'] = item.findtext('pubDate')

                # try these
                try:
                    episode['title'] = item.findtext('title')
                    episode['summary'] = item.findtext('description')
                except AttributeError:
                    # or try with itunes namespace
                    try:
                        episode['title'] = item.find('itunes:title', ns).text
                        episode['summary'] = item.xpath('itunes:summary', ns).text
                    # if episode data not found, skip
                    except AttributeError as e:
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.error('can\'t get episode data')
                        continue
                # try to get length
                try:
                    episode['length'] = item.find('itunes:duration', ns).text
                except AttributeError as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error('can\'t get length')
                    pass

                episode['podcast'] = self

                # link to episode
                # enclosure might be missing, have alternatives
                enclosure = item.find('enclosure')
                try:
                    episode['url'] = enclosure.get('url')
                    episode['type'] = enclosure.get('type')
                    episodes.append(episode)
                except AttributeError as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error('can\'t get episode url')
            return episodes

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

        # Genre.objects.all()
        genres = []
        for genre in genres:
            url = 'https://itunes.apple.com/us/rss/toppodcasts/limit=20/genre=' + str(genre.itunesid) + '/xml'

            r = requests.get(url, timeout=5)

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
                    # if podcast don't exists, scrape it and create it
                    except Podcast.DoesNotExist:
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.error('can\'t get pod')

                        podcast = Podcast.scrape_podcast(itunesid)
                        chart.append(podcast)

                return chart

            except requests.exceptions.HTTPError as e:
                print(str(e))

    def scrape_podcast(itunesid):
        """
        scrapes and returns podcast
        """

        # get data from itunes lookup
        url = 'https://itunes.apple.com/lookup?id=' + itunesid
        r = requests.get(url, timeout=5)
        try:
            r.raise_for_status()
            jsonresponse = r.json()
            data = jsonresponse['results'][0]
            itunesUrl = data['collectionViewUrl'].split('?')[0]
        except requests.exceptions.HTTPError as e:
            print('no response from lookup')
            return

        # get more data from itunes artist page
        r = requests.get(itunesUrl, timeout=5)
        try:
            r.raise_for_status()

            tree = html.fromstring(r.text)
            language = tree.xpath('//li[@class="language"]/text()')[0]
            podcastUrl = tree.xpath('//div[@class="extra-list"]/ul[@class="list"]/li/a/@href')[0]

            try:
                description = tree.xpath('//div[@class="product-review"]/p/text()')[0]
            except IndexError:
                description = ''

            try:
                copyrighttext = tree.xpath('//li[@class="copyright"]/text()')[0]
            except IndexError:
                copyrighttext = '© All rights reserved'

            try:
                itunesid = data['collectionId']
                feedUrl = data['feedUrl']
                title = data['collectionName']
                artist = data['artistName']
                artworkUrl = data['artworkUrl600'].replace('600x600bb.jpg', '')
                genre = data['primaryGenreName']
                explicit = True if data['collectionExplicitness'] == 'explicit' else False
                reviewsUrl = 'https://itunes.apple.com/us/rss/customerreviews/id=' + str(itunesid) + '/xml'

                genre = Genre.objects.get(name=genre)
                language = Language.create_or_get_language(language)

                # make sure feedUrl works
                r = requests.get(feedUrl, timeout=5)
                try:
                    r.raise_for_status()
                    try:
                        return Podcast.objects.get(itunesid=itunesid)
                    except Podcast.DoesNotExist:
                        return Podcast.objects.create(
                            itunesid=itunesid,
                            feedUrl=feedUrl,
                            title=title,
                            artist=artist,
                            genre=genre,
                            n_subscribers=0,
                            explicit=explicit,
                            language=language,
                            copyrighttext=copyrighttext,
                            description=description,
                            reviewsUrl=reviewsUrl,
                            artworkUrl=artworkUrl,
                            podcastUrl=podcastUrl,
                        )
                except requests.exceptions.HTTPError as e:
                    print('no response from feedUrl')
                    return
            except KeyError as e:
                print('Missing data: ' + str(e))

        except requests.exceptions.HTTPError as e:
            print('no response from itunes')

class Subscription(Podcast):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pod = models.ForeignKey('podcasts.Podcast', related_name='podcast')
    last_updated = models.DateTimeField(default=timezone.now)

    def get_subscriptions(user):
        subscriptions = Subscription.objects.filter(user=user)
        return subscriptions

    def get_subscriptions_itunesids(user):
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

    def create_or_update_genre(item):
        name = item['name']
        itunesid = item['itunesid']
        supergenre = item['supergenre']

        if supergenre:
            supergenre = Genre.objects.get(name=supergenre)
        try:
            genre = Genre.objects.get(name=name)
            genre.itunesid = itunesid
            genre.n_podcasts = 0
            genre.supergenre = supergenre
            genre.save()
        except Genre.DoesNotExist:
            Genre.objects.create(
                name=name,
                itunesid=itunesid,
                n_podcasts=0,
                supergenre=supergenre
            )

    def get_primary_genres():
        return Genre.objects.filter(supergenre=None).order_by('name')

    # after updating podcast database with scrapy, count n_podcasts
    def count_n_podcasts():
        genres = Genre.objects.all()
        for genre in genres:
            genre.n_podcasts = Podcast.objects.filter(genre=genre).count()
            if genre.supergenre == None:
                genre.n_podcasts += Podcast.objects.filter(genre__supergenre=genre).count()
            genre.save()

class Language(Filterable):

    def create_or_get_language(name):
        try:
            return Language.objects.get(name=name)
        except Language.DoesNotExist:
            return Language.objects.create(
                name=name,
                n_podcasts=0,
            )

    # after updating podcast database with scrapy, count n_podcasts
    def count_n_podcasts():
        languages = Language.objects.all()
        for language in languages:
            language.n_podcasts = Podcast.objects.filter(language=language).count()
            language.save()
