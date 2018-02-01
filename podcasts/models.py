from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.html import strip_tags
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.db.models import Q
from lxml import etree, html
from datetime import time, timedelta, datetime
from dateutil.parser import parse
import logging
import string
from urllib.parse import quote, unquote
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from fake_useragent import UserAgent

ua = UserAgent()

# https://www.peterbe.com/plog/best-practice-with-retries-with-requests
session = requests.Session()
retries=3
backoff_factor=0.3
status_forcelist=(500, 502, 504)
retry = Retry(
    total=retries,
    read=retries,
    connect=retries,
    backoff_factor=backoff_factor,
    status_forcelist=status_forcelist,
)
adapter = requests.adapters.HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)

logger = logging.getLogger(__name__)

def format_bytes(bytes):
    #2**10 = 1024
    power = 2**10
    suffixes = {1:'KB', 2:'MB', 3:'GB', 4:'TB'}

    n = 1
    if bytes <= power**2 :
        bytes /= power
        return '{0:4.1f}{1}'.format(bytes, suffixes[n])
    else:
        while bytes > power :
            n  += 1
            bytes /=  power**n
        return '{0:4.1f}{1}'.format(bytes, suffixes[n])

class Podcast(models.Model):
    podid = models.IntegerField(unique=True)
    feedUrl = models.CharField(max_length=1000)
    title = models.CharField(max_length=1000)
    artist = models.CharField(max_length=1000)
    genre = models.ForeignKey('podcasts.Genre', on_delete=models.CASCADE)
    explicit = models.BooleanField()
    language = models.ForeignKey('podcasts.Language', on_delete=models.CASCADE)
    copyrighttext = models.CharField(max_length=5000)
    description = models.TextField(max_length=5000, blank=True)
    n_subscribers = models.IntegerField(default=0)
    reviewsUrl = models.CharField(max_length=1000)
    artworkUrl = models.CharField(max_length=1000)
    podcastUrl = models.CharField(max_length=1000)
    discriminate = models.BooleanField(default=False)
    views = models.IntegerField(default=0)
    plays = models.IntegerField(default=0)
    rank = models.IntegerField(default=0)

    def __str__(self):
        return self.title

    def set_discriminated():
        bad_url = 'is4.mzstatic.com/image/thumb/Music6/v4/00/83/44/008344f6-7d9f-2031-39c1-107020839411/source/'
        bad_genre = Genre.objects.get(genreid=1314)

        for pod in Podcast.objects.filter(Q(artworkUrl=bad_url) | Q(genre=bad_genre)):
            pod.discriminate = True
            pod.save()

    def get_absolute_url(self):
        return reverse('podinfo', args='self.podid')

    def search(genre, language, user, q=None):
        """
        returns podcasts matching search terms
        """

        podcasts = Podcast.objects.all()

        # filter by explicit
        if user.is_authenticated:
            if not user.profile.show_explicit:
                podcasts = podcasts.filter(explicit=False)

        # filter by language
        if language:
            podcasts = podcasts.filter(language__name=language)

        # filter by genre
        if genre:
            podcasts = podcasts.filter(
                Q(genre__name=genre) |
                Q(genre__supergenre__name=genre)
            )

        # last but not least, filter by title
        if q:
            if len(q) > 1:
                podcasts = podcasts.filter(
                    Q(title__istartswith=q) |
                    Q(title__icontains=q)
                )
                podcasts = podcasts.order_by('rank', 'discriminate')
            else:
                if q == '#':
                    query = Q()
                    for letter in string.ascii_lowercase:
                        query = query | Q(title__istartswith=letter)
                        podcasts = podcasts.exclude(query)
                else:
                    the = 'the ' + q
                    podcasts = podcasts.filter(
                        Q(title__istartswith=q) |
                        Q(title__istartswith=the)
                    )
                podcasts = podcasts.order_by('title')
        else:
            podcasts = podcasts.filter().order_by('rank', 'discriminate')

        return podcasts

    def parse_itunes_charts(genre=None):
        """
        parses itunes chart xml data
        returns list of podcasts
        """

        headers = {
            'User-Agent': str(ua.random)
        }

        number = 100

        if genre:
            url = 'https://itunes.apple.com/us/rss/toppodcasts/limit=' + str(number) + '/genre=' + str(genre.genreid) + '/xml'
        else:
            url = 'https://itunes.apple.com/us/rss/toppodcasts/limit=' + str(number) + '/xml'

        try:
            response = session.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            root = etree.XML(response.content)

            ns = {'itunes': 'http://www.itunes.com/dtds/podcast-1.0.dtd',
                    'atom': 'http://www.w3.org/2005/Atom',
                    'im': 'http://itunes.apple.com/rss',
            }

            # delete None from namespaces, use atom instead
            ns.update(root.nsmap)
            del ns[None]

            podcasts = []

            for entry in root.findall('atom:entry', ns):
                element = entry.find('atom:id', ns)
                podid = element.xpath('./@im:id', namespaces=ns)[0]

                try:
                    podcast = Podcast.objects.get(podid=podid)
                # if podcast don't exists, scrape it and create it
                except Podcast.DoesNotExist:
                    logger.error('can\'t get pod, scraping')
                    podcast = Podcast.scrape_podcast(podid)
                if podcast:
                    podcasts.append(podcast)

        except requests.exceptions.HTTPError as e:
            logger.error(str(e))
        except requests.exceptions.ReadTimeout as e:
            logger.error('timed out')
        return podcasts

    def subscribe(self, user):
        """
        subscribes to or unsubscribes from podcast
        """

        # if subscription exists, delete it
        subscription, created = Subscription.objects.get_or_create(
            podcast=self,
            user=user,
        )
        if created:
            self.n_subscribers += 1
        else:
            subscription.delete()
            self.n_subscribers -= 1

    def set_subscribed(self, user):
        """
        sets self.is_subscribed = True if subscribed
        """

        self.is_subscribed = Subscription.objects.filter(user=user, podcast__podid=self.podid).exists()

    def scrape_podcast(podid):
        """
        uses itunes lookup to scrape podcast data
        """

        # useragent for requests
        headers = {
            'User-Agent': str(ua.random)
        }

        try:
            # get data from itunes lookup
            lookupUrl = 'https://itunes.apple.com/lookup?id=' + podid
            response = session.get(lookupUrl, headers=headers, timeout=10)
            response.raise_for_status()
            jsonresponse = response.json()
            data = jsonresponse['results'][0]
            itunesUrl = data['collectionViewUrl'].split('?')[0]
            podid = data['collectionId']
            feedUrl = data['feedUrl']
            title = data['collectionName']
            artist = data['artistName']
            artworkUrl = data['artworkUrl600'].replace('600x600bb.jpg', '')[7:]
            genre = data['primaryGenreName']
            explicit = True if data['collectionExplicitness'] == 'explicit' else False
            reviewsUrl = 'https://itunes.apple.com/us/rss/customerreviews/id=' + str(podid) + '/xml'

            # get more data from itunes artist page
            response = session.get(itunesUrl, headers=headers, timeout=10)
            response.raise_for_status()
            tree = html.fromstring(response.text)
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

            # make sure feedUrl works before creating podcast
            response = session.get(feedUrl, headers=headers, timeout=10)
            response.raise_for_status()
            genre = Genre.objects.get(name=genre)
            language = Language.objects.get_or_create(
                name=language,
            )
            podcast, created = Podcast.objects.get_or_create(
                podid=podid,
                feedUrl=feedUrl,
                title=title,
                artist=artist,
                genre=genre,
                explicit=explicit,
                language=language,
                copyrighttext=copyrighttext,
                description=description,
                reviewsUrl=reviewsUrl,
                artworkUrl=artworkUrl,
                podcastUrl=podcastUrl,
            )
            if created:
                logger.error('created podcast', title)
                logger.error('created podcast', feedUrl)
            else:
                logger.error('updated podcast', title)
                logger.error('updated podcast', feedUrl)
            return podcast
        except requests.exceptions.HTTPError as e:
            logger.error('no response from url:', feedUrl)
            return
        except requests.exceptions.ReadTimeout as e:
            logger.error('timed out:', feedUrl)
            return
        except KeyError as e:
            logger.error('Missing data: ' + str(e))
        except:
            # idna.core.IDNAError?
            logger.error('something else', lookupUrl, itunesUrl, feedUrl)
            return

class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscription')
    podcast = models.ForeignKey(Podcast, on_delete=models.CASCADE, related_name='subscription')
    last_updated = models.DateTimeField(default=timezone.now)
    new_episodes = models.IntegerField(default=0)

    class Meta:
        ordering = ('podcast__title',)

    def update(self):
        self.last_updated = timezone.now()

class Chart(models.Model):
    podcasts = models.ManyToManyField(Podcast, through='Order')
    size = models.IntegerField(default=0)
    provider = models.CharField(max_length=16)
    header = models.CharField(max_length=16, default='Top 50 podcasts')
    genre = models.ForeignKey('podcasts.Genre', null=True, default=None, on_delete=models.PROTECT)

    def set_charts():
        """
        sets genre_rank and global_rank for top ranking podcasts
        """

        # reviews https://itunes.apple.com/us/rss/customerreviews/id=xxx/xml

        number = 50
        genres = list(Genre.get_primary_genres())
        genres.append(None)

        for genre in genres:
            if genre:
                dopepod_charts = list(Podcast.objects.filter(genre=genre).order_by('discriminate', 'rank', 'n_subscribers', 'views', 'plays',))
            else:
                dopepod_charts = list(Podcast.objects.all().order_by('discriminate', 'rank', 'n_subscribers', 'views', 'plays',))
            itunes_charts = Podcast.parse_itunes_charts(genre)
            providers = [('dopepod', dopepod_charts[:number]), ('itunes', itunes_charts[:number])]
            for provider, podcasts in providers:
                size = len(podcasts)
                chart, created = Chart.objects.update_or_create(
                    provider=provider,
                    genre=genre,
                    defaults={
                        'size': size
                    },
                )

                Order.objects.filter(chart=chart).delete()

                for position, podcast in enumerate(podcasts, start=1):
                    Order.objects.create(
                        chart=chart,
                        podcast=podcast,
                        position=position,
                    )

    def get_charts(context, provider='itunes', genre=None, ajax=None):
        genres = Genre.get_primary_genres()
        chart = get_object_or_404(Chart, provider=provider, genre=genre)
        orders = Order.objects.filter(chart=chart).order_by('position')

        podcasts = []
        for order in orders:
            podcast = order.podcast
            podcast.position = order.position
            podcasts.append(podcast)

        url = '/charts/'
        urls = {}
        urls['q_url'] = url + '?'
        urls['genre_url'] = url + '?'
        urls['language_url'] = url + '?'
        urls['full_url'] = url + '?'

        results = {}
        results['drop'] = 'charts'
        results['podcasts'] = podcasts
        results['header'] = chart.header
        results['selected_genre'] = chart.genre
        results['genres'] = genres
        results['view'] = 'charts'
        results['urls'] = urls

        if ajax:
            context.update({
                'results': results,
            })
        else:
            context.update({
                'charts': results,
            })

        return context

class Order(models.Model):
    position = models.IntegerField()
    podcast = models.ForeignKey(Podcast, on_delete=models.PROTECT)
    chart = models.ForeignKey(Chart, on_delete=models.PROTECT)

class Episode(models.Model):
    podcast = models.ForeignKey(Podcast, on_delete=models.CASCADE)
    pubDate = models.DateTimeField()
    title = models.CharField(max_length=1000)
    summary = models.TextField(null=True, blank=True)
    length = models.DurationField(null=True, blank=True)
    url = models.CharField(max_length=1000)
    kind = models.CharField(max_length=16)
    size = models.CharField(max_length=16)
    played = models.DateTimeField(null=True, blank=True)

    def play(self):
        self.played = timezone.now()
        self.save()

    def played_ago(self):
        ago = timezone.now() - self.played
        seconds = ago.total_seconds()
        days = int(seconds // 86400)
        hours = int((seconds % 86400) // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        ago = ''
        if days:
            ago += str(days) + 'd '
        if hours:
            ago += str(hours) + 'h '
        if minutes:
            ago += str(minutes) + 'm '
        if seconds:
            ago += str(seconds) + 's '
        ago += ' ago'
        return ago

    def get_episodes(context, podcast, ajax=None):
        """
        returns a list of episodes using requests and lxml etree
        """

        ns = {'itunes': 'http://www.itunes.com/dtds/podcast-1.0.dtd',
            'atom': 'http://www.w3.org/2005/Atom',
            'im': 'http://itunes.apple.com/rss',
        }

        # useragent for requests
        headers = {
            'User-Agent': str(ua.random)
        }

        episodes = []

        try:
            response = session.get(podcast.feedUrl, headers=headers, timeout=5)
            response.raise_for_status()

            try:
                root = etree.XML(response.content)
                ns.update(root.nsmap)
                tree = root.find('channel')

                for item in tree.findall('item'):
                    episode = {}

                    # try to get pubdate + parse & convert it to datetime
                    try:
                        pubdate = item.find('pubDate').text
                        episode['pubDate'] = parse(pubdate)
                    # if episode data not found, skip episode
                    except AttributeError as e:
                        logger.error('can\'t get pubDate', podcast.feedUrl)
                        continue

                    # try to get title & summary
                    try:
                        episode['title'] = item.find('title').text
                        summary = item.find('description').text
                    except AttributeError:
                        # or try with itunes namespace
                        try:
                            summary = item.find('itunes:summary', ns).text
                        # if episode data not found, skip episode
                        except AttributeError as e:
                            logger.error('can\'t get title/description', podcast.feedUrl)
                            continue

                    # strip html tags+ split + join again by single space
                    episode['summary'] = ' '.join(strip_tags(summary).split())

                    # try to get length
                    try:
                        length = item.find('itunes:duration', ns).text
                    except AttributeError as e:
                        try:
                            length = item.find('duration').text
                        except AttributeError as e:
                            length = None
                            logger.error('can\'t get length', podcast.feedUrl)

                    if length:
                        # convert length to timedelta
                        if length.isdigit():
                            episode['length'] = timedelta(seconds=int(length))
                        else:
                            if '.' in length:
                                length = length.replace('.', ':')
                            try:
                                dt = datetime.strptime(length, '%H:%M:%S')
                                length = timedelta(hours=dt.hour, minutes=dt.minute, seconds=dt.second)
                                episode['length'] = length
                            except ValueError:
                                try:
                                    dt = datetime.strptime(length, '%M:%S')
                                    length = timedelta(minutes=dt.minute, seconds=dt.second)
                                    episode['length'] = length
                                except ValueError:
                                    logger.error('can\'t parse length', podcast.feedUrl)

                    episode['parent'] = podcast

                    # link to episode
                    # enclosure might be missing, have alternatives
                    enclosure = item.find('enclosure')
                    try:
                        episode['url'] = enclosure.get('url').replace('http:', '')
                        episode['type'] = enclosure.get('type')
                        episode['size'] = format_bytes(int(enclosure.get('length')))
                        episodes.append(episode)
                    except AttributeError as e:
                        logger.error('can\'t get episode url/type/size', podcast.feedUrl)

                context.update({
                    'episodes': episodes,
                })

                return context

            except etree.XMLSyntaxError:
                logger.error('trouble with xml')

        except requests.exceptions.HTTPError as e:
            logger.error(str(e))

    def get_last_played(context):
        last_played = Episode.objects.all().order_by('-played')[:20]
        context.update({
            'last_played': last_played,
        })
        return context

class Filterable(models.Model):
    """
    meta class for genre and language
    """

    name = models.CharField(primary_key=True, max_length=50)
    n_podcasts = models.IntegerField(default=0)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name

    def url_format(self):
        return quote(self.name)

    def unformat(self):
        return unquote(self.name)

    def count_n_podcasts():
        """
        after updating podcast database with scrapy, count and set n_podcasts
        """

        genres = Genre.objects.all()
        for genre in genres:
            genre.n_podcasts = Podcast.objects.filter(genre=genre).count()
            if genre.supergenre == None:
                genre.n_podcasts += Podcast.objects.filter(genre__supergenre=genre).count()
            genre.save()

        languages = Language.objects.all()
        for language in languages:
            language.n_podcasts = Podcast.objects.filter(language=language).count()
            language.save()

class Genre(Filterable):
    genreid = models.IntegerField()
    supergenre = models.ForeignKey('podcasts.Genre', on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        ordering = ('name',)

    def get_primary_genres():
        """
        returns primary genres
        """

        return Genre.objects.filter(supergenre=None)

class Language(Filterable):

    class Meta:
        ordering = ('-n_podcasts',)
