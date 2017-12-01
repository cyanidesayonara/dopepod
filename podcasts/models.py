from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from django.db.models import Q
import requests
from lxml import etree, html

class Podcast(models.Model):
    itunesid = models.IntegerField(primary_key=True)
    feedUrl = models.URLField(max_length=500)
    title = models.CharField(max_length=500)
    artist = models.CharField(max_length=500)
    genre = models.ForeignKey('podcasts.Genre')
    explicit = models.BooleanField()
    language = models.ForeignKey('podcasts.Language')
    copyrighttext = models.CharField(max_length=500)
    description = models.TextField(null=True, blank=True)
    n_subscribers = models.IntegerField(default=0)
    subscribed = models.BooleanField(default=False)
    reviewsUrl = models.URLField(max_length=500)
    artworkUrl = models.URLField(max_length=500)
    podcastUrl = models.URLField(max_length=500)
    genre_rank = models.IntegerField(null=True, blank=True)
    global_rank = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('podinfo', args='self.itunesid')

    def search(genre, language, explicit, user, q=None, alphabet=None):
        """
        return matching podcasts, set subscribed to True on subscribed ones
        """

        podcasts = Podcast.objects.all()

        # filter by explicit
        if explicit == False:
            podcasts = podcasts.filter(explicit=explicit)

        # filter by language
        if language != 'All':
            podcasts = podcasts.filter(language__name=language)

        # filter by genre
        if genre != 'All':
            podcasts = podcasts.filter(
                Q(genre__name=genre) |
                Q(genre__supergenre__name=genre)
            )

        # last but not least, filter by title
        if q:
            podcasts = podcasts.filter(
                Q(title__istartswith=q) |
                Q(title__icontains=q)
            )
        elif alphabet:
            podcasts = podcasts.filter(title__istartswith=alphabet).order_by('title')

        for podcast in podcasts:
            podcast.set_subscribed(user)
        return podcasts

    def set_ranks():
        """
        sets genre_rank and global_rank for top ranking podcasts
        """

        # reviews https://itunes.apple.com/us/rss/customerreviews/id=xxx/xml

        genres = Genre.get_primary_genres()

        # null all genre_ranks
        res1 = Podcast.objects.filter(genre_rank__isnull=False)
        res2 = Podcast.objects.filter(global_rank__isnull=False)
        podcasts = res1.union(res2)

        for podcast in podcasts:
            podcast.global_rank = None
            podcast.genre_rank = None
            podcast.save()

        for genre in genres:
            Podcast.parse_itunes_charts(genre)
        Podcast.parse_itunes_charts(None)

    def parse_itunes_charts(genre):
        if genre:
            url = 'https://itunes.apple.com/us/rss/toppodcasts/limit=100/genre=' + str(genre.itunesid) + '/xml'
        else:
            url = 'https://itunes.apple.com/us/rss/toppodcasts/limit=100/xml'

        try:
            r = requests.get(url, timeout=30)
            r.raise_for_status()

            root = etree.XML(r.content)

            ns = {'itunes': 'http://www.itunes.com/dtds/podcast-1.0.dtd',
                    'atom': 'http://www.w3.org/2005/Atom',
                    'im': 'http://itunes.apple.com/rss',
            }

            ns.update(root.nsmap)
            # delete None from namespaces, use atom instead
            del ns[None]

            for i, entry in enumerate(root.findall('atom:entry', ns), 1):
                element = entry.find('atom:id', ns)
                itunesid = element.xpath('./@im:id', namespaces=ns)[0]

                try:
                    podcast = Podcast.objects.get(itunesid=itunesid)
                # if podcast don't exists, scrape it and create it
                except Podcast.DoesNotExist:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error('can\'t get pod, scraping')
                    podcast = Podcast.scrape_podcast(itunesid)

                if podcast:
                    if genre:
                        podcast.genre_rank = i
                    else:
                        podcast.global_rank = i
                    podcast.save()
                else:
                    i = i -1

        except requests.exceptions.HTTPError as e:
            print(str(e))
        except requests.exceptions.ReadTimeout as e:
            print('timed out')

    def get_ranks(user, genre=None):

        if genre:
            podcasts = Podcast.objects.filter(genre=genre, genre_rank__isnull=False).order_by('genre_rank')
        else:
            podcasts = Podcast.objects.filter(global_rank__isnull=False) .order_by('global_rank')

        if user.is_authenticated:
            for podcast in podcasts:
                podcast.set_subscribed(user)

        return podcasts

    def subscribe(self, user):
        # if subscription exists, delete it
        try:
            subscription = Subscription.objects.get(parent=self, owner=user)
            subscription.delete()
            self.t.n_subscribers -= 1
            self.save()
            return False

        # if subscription doesn't exist, create it
        except Subscription.DoesNotExist:
            Subscription.objects.create(
                itunesid=self.itunesid,
                feedUrl=self.feedUrl,
                title=self.title,
                artist=self.artist,
                genre=self.genre,
                n_subscribers=self.n_subscribers,
                explicit=self.explicit,
                language=self.language,
                copyrighttext=self.copyrighttext,
                description=self.description,
                reviewsUrl=self.reviewsUrl,
                artworkUrl=self.artworkUrl,
                podcastUrl=self.podcastUrl,
                owner=user,
                parent=self,
            )
            self.n_subscribers += 1
            self.save()
            return True

    def set_subscribed(self, user):
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
        r = requests.get(feedUrl, timeout=5)

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

    def scrape_podcast(itunesid):
        """
        scrapes and returns podcast
        """

        # useragent for requests
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'
        }

        # get data from itunes lookup
        url = 'https://itunes.apple.com/lookup?id=' + itunesid
        try:
            r = requests.get(url, headers=headers, timeout=30)
            r.raise_for_status()
            jsonresponse = r.json()
            data = jsonresponse['results'][0]
            itunesUrl = data['collectionViewUrl'].split('?')[0]
        except requests.exceptions.HTTPError as e:
            print('no response from lookup')
            return

        # get more data from itunes artist page
        try:
            r = requests.get(itunesUrl, headers=headers, timeout=30)
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
                try:
                    r = requests.get(feedUrl, headers=headers, timeout=30)
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
                    print('no response from feedUrl:', feedUrl)
                    return
                except requests.exceptions.ReadTimeout as e:
                    print('timed out:', feedUrl)
                    return
            except KeyError as e:
                print('Missing data: ' + str(e))

        except requests.exceptions.HTTPError as e:
            print('no response from itunes')

class Subscription(Podcast):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    parent = models.ForeignKey('podcasts.Podcast', on_delete=models.CASCADE, related_name='podcast')
    last_updated = models.DateTimeField(default=timezone.now)
    new_episodes = models.IntegerField(default=0)

    def update(self):
        self.last_updated = timezone.now()

    def get_subscriptions(user):
        subscriptions = Subscription.objects.filter(owner=user)
        return subscriptions

    def get_subscriptions_itunesids(user):
        return Subscription.objects.filter(owner=user).values_list('itunesid', flat=True)

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
    itunesid = models.IntegerField()
    supergenre = models.ForeignKey('podcasts.Genre', on_delete=models.CASCADE, blank=True, null=True)

    def get_primary_genres():
        return Genre.objects.filter(supergenre=None).order_by('name')

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
                supergenre=supergenre
            )

class Language(Filterable):

    def create_or_get_language(name):
        try:
            return Language.objects.get(name=name)
        except Language.DoesNotExist:
            return Language.objects.create(
                name=name,
            )
