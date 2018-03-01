from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.html import strip_tags
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Q
from lxml import etree, html as lxml_html
from datetime import time, timedelta, datetime
from dateutil.parser import parse
import logging
import string
from urllib.parse import quote_plus, unquote_plus, urlencode
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from fake_useragent import UserAgent
from django.core import signing
from django.core.cache import cache
import re
import html
import idna

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
    description = models.TextField(max_length=5000, null=True, blank=True)
    n_subscribers = models.IntegerField(default=0)
    reviewsUrl = models.CharField(max_length=1000)
    artworkUrl = models.CharField(max_length=1000)
    podcastUrl = models.CharField(max_length=1000)
    discriminate = models.BooleanField(default=False)
    views = models.IntegerField(default=0)
    plays = models.IntegerField(default=0)
    rank = models.IntegerField(default=None, null=True)
    genre_rank = models.IntegerField(default=None, null=True)
    language_rank = models.IntegerField(default=None, null=True)
    itunes_rank = models.IntegerField(default=None, null=True)
    itunes_genre_rank = models.IntegerField(default=None, null=True)

    def get_primary_genre(self):
        return self.genre if self.genre.supergenre == None else self.genre.supergenre

    def get_n_subscribers(self):
        return str(self.n_subscribers) if self.n_subscribers > 100 else '<100'

    def __str__(self):
        return self.title

    def cache_index():
        Podcast.search()
        alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ#'

    def set_discriminated(self):
        bad_url = 'is4.mzstatic.com/image/thumb/Music6/v4/00/83/44/008344f6-7d9f-2031-39c1-107020839411/source/'
        bad_genre = Genre.objects.get(genreid=1314)

        if self.artworkUrl == bad_url or self.genre == bad_genre:
            self.discriminate = True
            self.save()

    def get_absolute_url(self):
        return reverse('podinfo', args='self.podid')

    def search(q, genre, language, page, show, view):
        """
        returns a tuple of (podcasts, num_pages and count) matching search terms
        """

        alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ#'
        languages = Language.objects.all()
        genres = Genre.get_primary_genres()

        cachestring = 'search'
        if q:
            cachestring += 'q=' + q
        if page:
            cachestring += 'page=' + str(page)
        if genre:
            cachestring += 'genre=' + genre.url_format()
        if language:
            cachestring += 'language=' + language.url_format()
        if show:
            cachestring += 'show=' + str(show)

        results = cache.get(cachestring)

        if results:
            return results
        else:
            podcasts = Podcast.objects.all()

            # filter by language
            if language:
                podcasts = podcasts.filter(language=language)

            # filter by genre
            if genre:
                podcasts = podcasts.filter(
                    Q(genre=genre) |
                    Q(genre__supergenre=genre)
                )

            # last but not least, filter by title
            if q:
                if len(q) > 1:
                    podcasts = podcasts.filter(
                        Q(title__istartswith=q) |
                        Q(title__icontains=q)
                    )
                else:
                    if q == '#':
                        query = Q()
                        for letter in string.ascii_lowercase:
                            query = query | Q(title__istartswith=letter)
                        podcasts = podcasts.exclude(query)
                    else:
                        podcasts = podcasts.filter(
                            Q(title__istartswith=q) |
                            Q(title__istartswith='the ' + q)
                        )
                    podcasts = podcasts.order_by('title')
            podcasts = podcasts.order_by('rank')

            end = show * page
            start = end - show
            count = podcasts.count()
            num_pages = int(count / show) + (count % show > 0)
            if end > count:
                end = count

            if not q:
                results_header = str(count) + ' podcasts'
            elif count == 1:
                results_header = str(count) + ' result for "' + q + '"'
            else:
                results_header = str(count) + ' results for "' + q + '"'

            url = '/search/'
            querystring = {}
            urls = {}

            if q:
                querystring['q'] = q
            if genre:
                querystring['genre'] = genre
            if language:
                querystring['language'] = language
            if view:
                querystring['view'] = view

            if q or genre or language:
                querystring_wo_q = {x: querystring[x] for x in querystring if x not in {'q'}}
                urls['q_url'] = url + '?' + urlencode(querystring_wo_q)

                querystring_wo_genre = {x: querystring[x] for x in querystring if x not in {'genre'}}
                urls['genre_url'] = url + '?' + urlencode(querystring_wo_genre)

                querystring_wo_language = {x: querystring[x] for x in querystring if x not in {'language'}}
                urls['language_url'] = url + '?' + urlencode(querystring_wo_language)

                urls['full_url'] = url + '?' + urlencode(querystring)
            else:
                urls['q_url'] = url + '?'
                urls['genre_url'] = url + '?'
                urls['language_url'] = url + '?'
                urls['full_url'] = url + '?'

            results = {}
            if num_pages > 1:
                pages = range((page - 2 if page - 2 > 1 else 1), (page + 2 if page + 2 <= num_pages else num_pages) + 1)
                results['pagination'] = {
                    'start': True if page != 1 else False,
                    'pages': pages,
                    'page': page,
                    'end': True if page != num_pages else False,
                }

            results['alphabet'] = alphabet
            results['podcasts'] = podcasts[:show]
            results['num_pages'] = num_pages
            results['count'] = count
            one = show // 4
            two = show // 2
            three = show // 2 + show // 4
            results['podcasts1'] = results['podcasts'][:one]
            results['podcasts2'] = results['podcasts'][one:two]
            results['podcasts3'] = results['podcasts'][two:three]
            results['podcasts4'] = results['podcasts'][three:]

            results['header'] = results_header
            results['selected_q'] = q
            results['selected_genre'] = genre
            results['selected_language'] = language
            results['genres'] = genres
            results['languages'] = languages
            results['view'] = view
            results['urls'] = urls
            results['extra_options'] = True

            cache.set(cachestring, results, 60 * 60 * 24)
            return results

    def subscribe_or_unsubscribe(self, user):
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
        self.save()

    def unsubscribe(self, user):
        """
        subscribes to or unsubscribes from podcast
        """

        # if subscription exists, delete it
        subscription = Subscription.objects.get(
            podcast=self,
            user=user,
        )
        subscription.delete()
        self.n_subscribers -= 1
        self.save()

    def is_subscribed(self, user):
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
            response = requests.get(lookupUrl, headers=headers, timeout=10)
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
            response = requests.get(itunesUrl, headers=headers, timeout=10)
            response.raise_for_status()
            tree = lxml_html.fromstring(response.text)
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
            response = requests.get(feedUrl, headers=headers, timeout=10)
            response.raise_for_status()
            genre, created = Genre.objects.get_or_create(
                name=genre
            )
            language, created = Language.objects.get_or_create(
                name=language,
            )
            podcast, created = Podcast.objects.update_or_create(
                podid=podid,
                defaults={
                    'feedUrl': feedUrl,
                    'title': title,
                    'artist': artist,
                    'genre': genre,
                    'explicit': explicit,
                    'language': language,
                    'copyrighttext': copyrighttext,
                    'description': description,
                    'reviewsUrl': reviewsUrl,
                    'artworkUrl': artworkUrl,
                    'podcastUrl': podcastUrl,
                }
            )
            if created:
                logger.error('created podcast', title, feedUrl)
            else:
                logger.error('updated podcast', title, feedUrl)
            podcast.set_discriminated()
            return podcast

        except requests.exceptions.HTTPError:
            logger.error('no response from url:', feedUrl)
        except requests.exceptions.ReadTimeout:
            logger.error('timed out:', feedUrl)
        except requests.exceptions.InvalidSchema:
            logger.error('invalid schema:', feedUrl)
        except idna.IDNAError:
            logger.error('goddam idna error', feedUrl)
        except KeyError:
            logger.error('Missing data: ', feedUrl)

    def set_charts():
        """
        sets genre_rank and global_rank for top ranking podcasts
        """

        # TODO parse reviews
        # reviews https://itunes.apple.com/us/rss/customerreviews/id=xxx/json

        genres = list(Genre.get_primary_genres())
        genres.append(None)

        for genre in genres:
            # list of episodes parsed from itunes charts
            podcasts = Podcast.parse_itunes_charts(genre)

            # set ranks to None
            if podcasts:
                if genre:
                    for podcast in Podcast.objects.filter(genre=genre).exclude(itunes_genre_rank=None):
                        podcast.itunes_genre_rank = None
                        podcast.save()
                else:
                    for podcast in Podcast.objects.all().exclude(itunes_rank=None):
                        podcast.itunes_rank = None
                        podcast.save()

            for i, podcast in enumerate(podcasts, start=1):
                if genre:
                    podcast.itunes_genre_rank = i
                else:
                    podcast.itunes_rank = i
                podcast.save()

            podcasts = Podcast.objects.all()
            if genre:
                podcasts = podcasts.filter(
                    Q(genre=genre) |
                    Q(genre__supergenre=genre)
                )
            podcasts = podcasts.order_by(
                'discriminate', '-n_subscribers', '-views', '-plays', 'rank', 'itunes_rank', 'itunes_genre_rank'
            )

            for podcast in podcasts:
                if genre:
                    podcast.genre_rank = None
                else:
                    podcast.rank = None

            for i, podcast in enumerate(podcasts, start=1):
                if genre:
                    podcast.genre_rank = i
                else:
                    podcast.rank = i
                podcast.save()

        for language in Language.objects.all():
            podcasts = Podcast.objects.filter(language=language).order_by(
                'discriminate', '-n_subscribers', '-views', '-plays', 'rank', 'itunes_rank', 'itunes_genre_rank'
            )
            for podcast in podcasts:
                podcast.language_rank = None

            for i, podcast in enumerate(podcasts, start=1):
                podcast.language_rank = i
                podcast.save()

    def parse_itunes_charts(genre=None):
        """
        parses itunes chart xml data
        returns list of podcasts
        """

        headers = {
            'User-Agent': str(ua.random)
        }

        # number of chart entries to list, 100 seems to be max
        number = 100
        podcasts = []

        # urls to use
        if genre:
            url = 'https://itunes.apple.com/us/rss/topaudiopodcasts/limit=' + str(number) + '/genre=' + str(genre.genreid) + '/json'
        else:
            url = 'https://itunes.apple.com/us/rss/topaudiopodcasts/limit=' + str(number) + '/json'

        try:
            response = session.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            jsonresponse = response.json()

            # iterate thru every entry, extract podid
            for x in jsonresponse['feed']['entry']:
                podid = x['id']['attributes']['im:id']

                if podid:
                    try:
                        podcast = Podcast.objects.get(podid=podid)
                    # if podcast don't exists, scrape it and create it
                    # TODO maybe use this to update pods every time
                    except Podcast.DoesNotExist:
                        logger.error('can\'t get pod, scraping')
                        podcast = Podcast.scrape_podcast(podid)

                    if podcast:
                        podcasts.append(podcast)

        except requests.exceptions.HTTPError as e:
            logger.error('http error', url)
        except requests.exceptions.ReadTimeout:
            logger.error('timed out', url)
        except requests.exceptions.RetryError:
            logger.error('too many retries:', url)
        return podcasts

    def cache_charts():
        genres = list(Genre.get_primary_genres())
        genres.append(None)

        for provider in ['dopepod', 'itunes']:
            if provider == 'dopepod':
                languages = list(Language.objects.all())
                languages.append(None)
            else:
                languages = [None]
            for language in languages:
                for genre in genres:
                    Podcast.get_charts(provider, genre, language, True)

    def get_charts(provider='dopepod', genre=None, language=None, force_cache=False):
        cachestring = 'charts'
        if provider:
            cachestring += 'provider=' + provider
        if genre:
            cachestring += 'genre=' + str(genre).replace(' ', '')
        if language:
            cachestring += 'language=' + str(language).replace(' ', '')
        results = cache.get(cachestring)
        if results and not force_cache:
            return results
        else:
            genres = Genre.get_primary_genres()
            podcasts = Podcast.objects.all()
            languages = None
            if provider == 'dopepod':
                languages = Language.objects.all()
                if not genre and not language:
                    podcasts = podcasts.order_by('rank')
                if genre:
                    podcasts = podcasts.filter(
                        Q(genre=genre) |
                        Q(genre__supergenre=genre)
                    )
                    if not language:
                        podcasts = podcasts.order_by('genre_rank')
                if language:
                    podcasts = podcasts.filter(language=language).order_by('language_rank')
            if provider == 'itunes':
                if genre:
                    podcasts = podcasts.exclude(itunes_genre_rank=None).filter(
                        Q(genre=genre) |
                        Q(genre__supergenre=genre)
                    ).order_by('itunes_genre_rank')
                else:
                    podcasts = podcasts.exclude(itunes_rank=None).order_by('itunes_rank')
            if podcasts:
                podcasts = podcasts[:50]
            else:
                genre = None
                return Podcast.get_charts(provider, genre, language)

            url = '/charts/'
            querystring = {}
            urls = {}

            if provider:
                querystring['provider'] = provider
            if genre:
                querystring['genre'] = genre
            if language:
                querystring['language'] = language

            querystring_wo_provider = {x: querystring[x] for x in querystring if x not in {'provider'}}
            urls['provider_url'] = url + '?' + urlencode(querystring_wo_provider)

            querystring_wo_genre = {x: querystring[x] for x in querystring if x not in {'genre'}}
            urls['genre_url'] = url + '?' + urlencode(querystring_wo_genre)

            querystring_wo_language = {x: querystring[x] for x in querystring if x not in {'language'}}
            urls['language_url'] = url + '?' + urlencode(querystring_wo_language)

            urls['full_url'] = url + '?' + urlencode(querystring)

            results = {}
            results['drop'] = '-charts'
            results['podcasts'] = podcasts
            results['header'] = 'Top ' + str(len(podcasts)) + ' podcasts'
            results['providers'] = ['dopepod', 'itunes']
            results['selected_provider'] = provider
            results['genres'] = genres
            results['selected_genre'] = genre
            if languages:
                results['languages'] = languages
                results['selected_language'] = language
            results['view'] = 'charts'
            results['urls'] = urls
            cache.add(cachestring, results, 60 * 60 * 24)
            return results

class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscription')
    podcast = models.ForeignKey(Podcast, on_delete=models.CASCADE, related_name='subscription')
    last_updated = models.DateTimeField(null=True, default=None)
    new_episodes = models.IntegerField(default=0)

    class Meta:
        ordering = ('podcast__title',)

    def update(self):
        self.last_updated = timezone.now()
        self.save()

    def get_subscriptions(user):
        subscriptions = Subscription.objects.filter(user=user)
        if subscriptions.count() == 1:
            results_header = str(subscriptions.count()) + ' subscription'
        else:
            results_header = str(subscriptions.count()) + ' subscriptions'

        results = {}
        results['podcasts'] = subscriptions
        results['header'] = results_header
        results['view'] = 'subscriptions'
        results['subscriptions'] = True
        results['extra_options'] = True
        return results

class Episode(models.Model):
    pubDate = models.DateTimeField()
    title = models.CharField(max_length=1000)
    description = models.TextField(max_length=5000, null=True, blank=True)
    length = models.DurationField(null=True, blank=True)
    url = models.CharField(max_length=1000)
    kind = models.CharField(max_length=16)
    size = models.CharField(null=True, blank=True, max_length=16)
    signature = models.CharField(max_length=5000)

    class Meta:
        abstract = True

    def get_episodes(podcast):
        """
        returns a list of episodes using requests and lxml etree
        """

        episodes = cache.get(podcast.podid)
        if episodes:
            return episodes
        else:
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
                            pubdate = parse(pubdate, default=parse("00:00Z"))
                            episode['pubDate'] = datetime.strftime(pubdate,"%b %d %Y %X %z")
                        # if episode data not found, skip episode
                        except AttributeError as e:
                            logger.error('can\'t get pubDate', podcast.feedUrl)
                            continue

                        # try to get title & description
                        try:
                            episode['title'] = item.find('title').text
                        except AttributeError:
                            try:
                                episode['title'] = item.find('itunes:subtitle').text
                            except AttributeError as e:
                                logger.error('can\'t get title', podcast.feedUrl)
                                continue
                        try:
                            description = item.find('description').text
                        except AttributeError:
                            # or try with itunes namespace
                            try:
                                description = item.find('itunes:summary', ns).text
                            # if episode data not found, skip episode
                            except AttributeError as e:
                                description = ''
                                logger.error('can\'t get description', podcast.feedUrl)

                        if not description:
                            description = ''
                        else:
                            description = html.unescape(description)

                        # strip html tags+ split + join again by single space
                        episode['description'] = ' '.join(strip_tags(description).split())

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
                            if length.isdigit() and length != 0:
                                delta = timedelta(seconds=int(length))
                                episode['length'] = str(delta)
                            else:
                                if re.search('[1-9]', length):
                                    if '.' in length:
                                        length = length.split('.')
                                    elif ':' in length:
                                        length = length.split(':')

                                    try:
                                        hours = int(length[0])
                                        minutes = int(length[1])
                                        seconds = int(length[2])
                                        delta = timedelta(hours=hours, minutes=minutes, seconds=seconds)
                                        episode['length'] = str(delta)
                                    except (ValueError, IndexError):
                                        try:
                                            minutes = int(length[0])
                                            seconds = int(length[1])
                                            delta = timedelta(minutes=minutes, seconds=seconds)
                                            episode['length'] = str(delta)
                                        except (ValueError, IndexError):
                                            logger.error('can\'t parse length', podcast.feedUrl)

                        episode['podid'] = podcast.podid

                        # link to episode
                        # enclosure might be missing, have alternatives
                        enclosure = item.find('enclosure')
                        try:
                            size = enclosure.get('length')
                            if size and int(size) > 1:
                                episode['size'] = format_bytes(int(size))
                        except (AttributeError, ValueError):
                            logger.error('can\'t get episode size', podcast.feedUrl)

                        try:
                            episode['url'] = enclosure.get('url').replace('http:', '')
                            episode['type'] = enclosure.get('type')

                            # create signature
                            episode['signature'] = signing.dumps(episode)
                            episode['pubDate'] = pubdate
                            episodes.append(episode)
                        except AttributeError as e:
                            logger.error('can\'t get episode url/type/size', podcast.feedUrl)

                except etree.XMLSyntaxError:
                    logger.error('trouble with xml')

            except requests.exceptions.HTTPError as e:
                logger.error(str(e))
            cache.set(podcast.podid, episodes, 60 * 60)
            return episodes

    def set_new(user, podcast, episodes):
        if user.is_authenticated:
            try:
                subscription = Subscription.objects.get(user=user, podcast=podcast)
                i = 0
                for episode in episodes:
                    if not subscription.last_updated:
                        pass
                    elif subscription.last_updated < episode['pubDate']:
                        pass
                    else:
                        continue
                    i += 1
                    episode['is_new'] = True
                subscription.last_updated = timezone.now()
                subscription.new_episodes = i
                subscription.save()
            except Subscription.DoesNotExist:
                pass
        return episodes

class Played_Episode(Episode):
    podcast = models.ForeignKey(Podcast, on_delete=models.CASCADE, related_name='played_episode')
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name='played_episode')
    played_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ('-played_at',)

    def play(self):
        self.podcast.plays += 1
        self.podcast.save()

    def played_ago(self):
        ago = timezone.now() - self.played_at
        seconds = ago.total_seconds()
        days = int(seconds // (60 * 60 * 24))
        hours = int((seconds % (60 * 60 * 24)) // (60 * 60))
        minutes = int((seconds % (60 * 60)) // 60)
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

    def get_last_played():
        last_played = Played_Episode.objects.all()

        results = {}
        results['episodes'] = last_played
        results['header'] = 'Last played'
        results['view'] = 'last_played'
        return results

@receiver(post_save, sender=Played_Episode)
def limit_episodes(sender, instance, created, **kwargs):
    if created:
        wannakeep = Played_Episode.objects.all()[:50]
        Played_Episode.objects.exclude(pk__in=wannakeep).delete()

class Playlist_Episode(Episode):
    podcast = models.ForeignKey(Podcast, on_delete=models.CASCADE, related_name='playlist_episode')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='playlist_episode')
    added_at = models.DateTimeField(default=timezone.now)

    def delete_from_playlist():
        Playlist_Episode.objects.filter(user=user).order_by('-added_at')

    def get_playlist(user):
        playlist = Playlist_Episode.objects.filter(user=user).order_by('-added_at')
        if playlist.count() == 1:
            results_header = str(playlist.count()) + ' episode'
        else:
            results_header = str(playlist.count()) + ' episodes'

        results = {}
        results['episodes'] = playlist
        results['header'] = results_header
        results['view'] = 'playlist'
        results['extra_options'] = True
        return results

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
        return quote_plus(self.name)

    def unformat(self):
        return unquote_plus(self.name)

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

# class SearchTerm(models.Model):
#     number = models.IntegerField()
#     text = models.CharField(max_length=100)
#
#     class Meta:
#         ordering = ('number',)
