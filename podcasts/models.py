from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.html import strip_tags
from django.urls import reverse
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import F, Q, Max
from lxml import etree, html as lxml_html
from datetime import time, timedelta, datetime
from dateutil.parser import parse
from urllib.parse import quote_plus, unquote_plus, urlencode
from furl import furl
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from fake_useragent import UserAgent
from django.core import signing
from django.core.cache import cache
from django.db import transaction
from haystack.query import SearchQuerySet
from plotly.graph_objs import Pie
import plotly
import logging
import string
import requests
import time
import re
import html
import idna
import copy
logger = logging.getLogger(__name__)

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
session.mount("http://", adapter)
session.mount("https://", adapter)

def donuts():
    names = list(Genre.get_primary_genres().values_list("name", flat=True))
    numbers = list(Genre.get_primary_genres().values_list("n_podcasts", flat=True))
    plotly.offline.plot({
        "data": [
            {
                "labels": names,
                "values": numbers,
                "name": "",
                "hoverinfo":"label+percent+name",
                "hole": .4,
                "type": "pie",
            }
        ],
        "layout": {
            "annotations": [
                {
                    "font": {
                        "size": 20
                    },
                    "showarrow": False,
                    "text": "Genres",
                    "x": 0.5,
                    "y": 0.5
                },
            ]
        }
    }, filename='donut.html')

def format_bytes(bytes):
    #2**10 = 1024
    power = 2**10
    suffixes = {1:"KB", 2:"MB", 3:"GB", 4:"TB"}

    n = 1
    if bytes <= power**2 :
        bytes /= power
        return "{0:4.1f}{1}".format(bytes, suffixes[n])
    else:
        while bytes > power :
            n  += 1
            bytes /=  power**n
        return "{0:4.1f}{1}".format(bytes, suffixes[n])

def make_url(url, provider=None, q=None, genre=None, language=None, show=None, page=None, view=None):
    f = furl(url)
    f.args.clear()

    if provider:
        f.path = "/charts/"
        f.args["provider"] = provider
    if q:
        f.args["q"] = q
    if genre:
        f.args["genre"] = genre
    if language:
        f.args["language"] = language
    if show:
        f.args["show"] = show
    if page:
        f.args["page"] = page
    if view:
        f.args["view"] = view
    return f.url

class PodcastManager(models.Manager):
    def get_queryset(self):
        return super(PodcastManager, self).get_queryset().select_related("genre", "genre__supergenre", "language")

class Podcast(models.Model):
    podid = models.IntegerField(unique=True)
    feedUrl = models.CharField(max_length=1000)
    title = models.CharField(max_length=1000)
    artist = models.CharField(max_length=1000)
    genre = models.ForeignKey("podcasts.Genre", on_delete=models.CASCADE, related_name="podcast")
    explicit = models.BooleanField()
    language = models.ForeignKey("podcasts.Language", on_delete=models.CASCADE, related_name="podcast")
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

    objects = PodcastManager()

    def __str__(self):
        return self.title

    def get_primary_genre(self):
        return self.genre if self.genre.supergenre == None else self.genre.supergenre

    def get_n_subscribers(self):
        if type(self.n_subscribers) == int:
            return str(self.n_subscribers) if self.n_subscribers > 100 else "<1k"
        else:
            return "<1k"

    def set_discriminated(self):
        bad_url = "is4.mzstatic.com/image/thumb/Music6/v4/00/83/44/008344f6-7d9f-2031-39c1-107020839411/source/"
        bad_genre = Genre.objects.get(genreid=1314)

        if self.artworkUrl == bad_url or self.genre == bad_genre:
            self.discriminate = True
            self.save()

    def get_absolute_url(self):
        return reverse("podinfo", args="self.podid")

    def search(url, provider=None, q=None, genre=None, language=None, show=None, page=None, view=None, force_cache=False):
        """
        returns podcasts matching search terms
        """
        
        # make url for cache string
        url = make_url(url=url, provider=provider, q=q, genre=genre, language=language,
                       show=show, page=page)

        # if cached, return results
        results = cache.get(url)

        if results and not force_cache:
            return results
        else:
            podcasts = SearchQuerySet().all().load_all()

            # filter by language
            if language:
                podcasts = podcasts.filter(language__exact=language)

            # filter by genre
            if genre:
                podcasts = podcasts.filter(genre__exact=genre)

            # SEARCH
            # filter by title
            if q:
                if len(q) > 1:
                    podcasts = podcasts.filter(content__contains=q).order_by("rank")
                else:
                    # exclude pods not starting w/ an alphabet
                    if q == "#":
                        query = Q()
                        for letter in string.ascii_lowercase:
                            query = query | Q(initial__exact=letter * 2)
                        podcasts = podcasts.exclude(query)
                    # filter pods starting w/ an alphabet
                    else:
                        podcasts = podcasts.filter(initial__exact=q * 2)
                    podcasts = podcasts.order_by("title_rank")

            # CHARTS
            elif provider == "dopepod":
                if language:
                    podcasts = podcasts.order_by("language_rank")
                elif genre:
                    podcasts = podcasts.order_by("genre_rank")
                else:
                    podcasts = podcasts.order_by("rank")
            elif provider == "itunes":
                if genre:
                    podcasts = podcasts.exclude(_missing_="itunes_genre_rank").order_by("itunes_genre_rank")
                else:

                    podcasts = podcasts.exclude(_missing_="itunes_rank").order_by("itunes_rank")
            else:
                podcasts = podcasts.order_by("rank")

            results = {}

            # if not provider, make alphabet
            if provider:
                alphabet = ""
            else:
                alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ#"
                alphabet_urls = []

            genres = Genre.get_primary_genres()
            genres_urls = []
            if provider == "itunes":
                languages = []
                language = None
            else:
                languages = Language.get_languages()
                languages_urls = []

            if not provider:
                # create urls for buttons
                # starting with alphabet
                url = make_url(url=url, q="x", genre=genre, language=language,
                            show=show, view=view)
                for alpha in alphabet:
                    if alpha.lower() == q:
                        alphabet_urls.append(None)
                    else:
                        f = furl(url)
                        f.args["q"] = alpha
                        alphabet_urls.append(f.url)
                if q:
                    results["selected_q"] = q
                    if len(q) == 1:
                        f = furl(url)
                        del f.args["q"]
                        results["alphabet_nix_url"] = f.url

            # genre buttons
            url = make_url(url=url, provider=provider, q=q, genre="x", language=language,
                        show=show, view=view)
            for gen in genres:
                if gen == genre:
                    genres_urls.append(None)
                else:
                    f = furl(url)
                    f.args["genre"] = gen
                    genres_urls.append(f.url)
            if genre:
                results["selected_genre"] = genre

                f = furl(url)
                del f.args["genre"]
                results["genre_nix_url"] = f.url

            # language buttons
            url = make_url(url=url, provider=provider, q=q, genre=genre, language="x",
                        show=show, view=view)
            for lang in languages:
                if lang == language:
                    languages_urls.append(None)
                else:
                    f = furl(url)
                    f.args["language"] = lang
                    languages_urls.append(f.url)
            if language:
                results["selected_language"] = language
                f = furl(url)
                del f.args["language"]
                results["language_nix_url"] = f.url

            # provider button
            url = make_url(url=url, provider=provider, q=q, genre=genre, 
                        show=show, page=page, view=view)
            if provider:
                view = "charts"
                f = furl(url)
                if provider == "dopepod":
                    f.args["provider"] = "itunes"
                else:
                    f.args["provider"] = "dopepod"
                results["provider_url"] = f.url

            url = make_url(url=url, provider=provider, q=q, genre=genre, language=language,
                show=show, page=page, view=view)
            
            # view button
            if not view:
                if q and len(q) > 1:
                    view = "grid"
                else:
                    view = "list" 

                f = furl(url)
                if view == "grid":
                    f.args["view"] = "list"
                else:
                    f.args["view"] = "grid"
                results["view_url"] = f.url
            
            results["view"] = view

            # zip button text w/ url
            results["genres"] = zip(genres, genres_urls)
            if not provider:
                results["alphabet"] = zip(alphabet, alphabet_urls)
            if not provider == "itunes":
                results["languages"] = zip(languages, languages_urls)

            url = make_url(url=url, provider=provider, q=q, genre=genre, language=language,
                            show=show, page=page, view=view)

            # finally, the real url
            results["full_url"] = url

            # if charts
            if provider:
                # show top {number here}
                if not show:
                    show = 50
                podcasts = podcasts[:show]
                count = len(podcasts)
                # if no results, try w/o language
                if not podcasts:
                    url = make_url(url=url, provider=provider,
                                   language=language)
                    return Podcast.search(url=url, provider=provider, language=language, view=view)
            # if search
            else:
                if not page:
                    page = 1
                if not show:
                    show = 120
                count = podcasts.count()
            
            # charts header
            if provider:
                results["podcasts"] = podcasts
                results["header"] = "Top " + str(count) + " podcasts"
                results["providers"] = ["dopepod", "itunes"]
                results["selected_provider"] = provider
            # search header & pages
            else:
                num_pages = int(count / show) + (count % show > 0)

                spread = 3
                if num_pages > 1:
                    pages = range((page - spread if page - spread > 1 else 1), (page + spread if page + spread <= num_pages else num_pages) + 1)
                    pages_urls = []
                    
                    for p in pages:
                        if p == page:
                            pages_urls.append(None)
                        else:
                            f = furl(url)
                            f.args["page"] = p
                            pages_urls.append(f.url)
                    #  zip pages & use list to make it reusable
                    results["pages"] = list(zip(pages, pages_urls))

                    if page < num_pages - spread:
                        f = furl(url)
                        f.args["page"] = num_pages
                        results["end_url"] = f.url
                    
                    if page > 1 + spread:
                        f = furl(url)
                        del f.args["page"]
                        results["start_url"] = f.url
                
                if not q:
                    results_header = "Browsing " + str(count) + " podcasts"
                elif count == 1:
                    results_header = str(count) + " result for \"" + q + "\""
                else:
                    results_header = str(count) + " results for \"" + q + "\""
                results["header"] = results_header

                # show selected page
                podcasts = podcasts[(page - 1) * show:page * show]

                results["num_pages"] = num_pages
                results["count"] = count
                one = show // 4
                two = show // 2
                three = show // 2 + show // 4
                results["podcasts1"] = podcasts[:one]
                results["podcasts2"] = podcasts[one:two]
                results["podcasts3"] = podcasts[two:three]
                results["podcasts4"] = podcasts[three:]

                results["extra_options"] = True

            # finally (finally!) cache results so we don"t have to go thru this every time
            cache.set(url, results, 60 * 60 * 24)
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
            self.n_subscribers = F("n_subscribers") + 1
        else:
            subscription.delete()
            self.n_subscribers = F("n_subscribers") - 1
        self.save()

    def is_subscribed(self, user):
        """
        sets self.is_subscribed = True if subscribed
        """
        if user.is_authenticated:
            self.is_subscribed = Subscription.objects.filter(user=user, podcast__podid=self.podid).exists()

    def scrape_podcast(podid):
        """
        uses itunes lookup to scrape podcast data
        """

        # useragent for requests
        headers = {
            "User-Agent": str(ua.random)
        }
        logger.error("scraping", podid)
        try:
            # get data from itunes lookup
            lookupUrl = "https://itunes.apple.com/lookup?id=" + podid
            response = requests.get(lookupUrl, headers=headers, timeout=10)
            response.raise_for_status()
            jsonresponse = response.json()
            data = jsonresponse["results"][0]
            itunesUrl = data["collectionViewUrl"].split("?")[0]
            podid = data["collectionId"]
            feedUrl = data["feedUrl"]
            title = data["collectionName"]
            artist = data["artistName"]
            artworkUrl = data["artworkUrl600"].replace("600x600bb.jpg", "")[7:]
            genre = data["primaryGenreName"]
            explicit = True if data["collectionExplicitness"] == "explicit" else False
            reviewsUrl = "https://itunes.apple.com/us/rss/customerreviews/id=" + str(podid) + "/json"

            # get more data from itunes artist page
            response = requests.get(itunesUrl, headers=headers, timeout=10)
            response.raise_for_status()
            tree = lxml_html.fromstring(response.text)
            language = tree.xpath("//li[@class='language']/text()")[0]
            
            podcastUrl = tree.xpath("//div[@class='extra-list']/ul[@class='list']/li/a/@href")[0]
            try:
                if podcastUrl[:2] == "//" or podcastUrl[:4] == "http":
                    pass
                elif podcastUrl[:1] == "/" or "." not in podcastUrl:
                    podcastUrl == ""
                else:
                    podcastUrl = "//" + podcastUrl
            except IndexError:
                pass

            try:
                description = tree.xpath("//div[@class='product-review']/p/text()")[0]
            except IndexError:
                description = ""

            try:
                copyrighttext = tree.xpath("//li[@class='copyright']/text()")[0]
            except IndexError:
                copyrighttext = "© All rights reserved"

            try:
                # make sure feedUrl works before creating podcast
                response = requests.get(feedUrl, headers=headers, timeout=10)
                response.raise_for_status()

                genre, created = Genre.objects.get_or_create(
                    name=genre
                )
                language, created = Language.objects.get_or_create(
                    name=language,
                )

                # TODO try to get episodes before creating podcast 

                with transaction.atomic():
                    podcast, created = Podcast.objects.select_related(None).select_for_update().update_or_create(
                        podid=podid,
                        defaults={
                            "feedUrl": feedUrl,
                            "title": title,
                            "artist": artist,
                            "genre": genre,
                            "explicit": explicit,
                            "language": language,
                            "copyrighttext": copyrighttext,
                            "description": description,
                            "reviewsUrl": reviewsUrl,
                            "artworkUrl": artworkUrl,
                            "podcastUrl": podcastUrl,
                        }
                    )
                    if created:
                        logger.error("created podcast", title, feedUrl)
                    else:
                        logger.error("updated podcast", title, feedUrl)
                    podcast.set_discriminated()
                    return podcast

            except requests.exceptions.TooManyRedirects:
                logger.error("too many redirects", feedUrl)
            except requests.exceptions.HTTPError:
                logger.error("http error", feedUrl)
            except requests.exceptions.ReadTimeout:
                logger.error("timed out", feedUrl)
            except requests.exceptions.ConnectTimeout:
                logger.error("timed out", feedUrl)
            except requests.exceptions.RetryError:
                logger.error("too many retries:", feedUrl)

        except requests.exceptions.HTTPError:
            logger.error("no response from url:", feedUrl)
        except requests.exceptions.ReadTimeout:
            logger.error("timed out:", feedUrl)
        except requests.exceptions.InvalidSchema:
            logger.error("invalid schema:", feedUrl)
        except idna.IDNAError:
            logger.error("goddam idna error", feedUrl)
        except KeyError:
            logger.error("Missing data: ", feedUrl)

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
                    for podcast in Podcast.objects.exclude(itunes_rank=None):
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
                "discriminate", "-n_subscribers", "-views", "-plays", "itunes_rank", "itunes_genre_rank", "rank"
            )
            for i, podcast in enumerate(podcasts, start=1):
                if genre:
                    podcast.genre_rank = i
                else:
                    podcast.rank = i
                podcast.save()

        for language in Language.get_languages():
            podcasts = Podcast.objects.filter(language=language).order_by(
                "discriminate", "-n_subscribers", "-views", "-plays", "itunes_rank", "itunes_genre_rank", "rank"
            )
            for i, podcast in enumerate(podcasts, start=1):
                podcast.language_rank = i
                podcast.save()

    def parse_itunes_charts(genre=None):
        """
        parses itunes chart json data
        returns list of podcasts
        """

        headers = {
            "User-Agent": str(ua.random)
        }

        # number of chart entries to list, 100 seems to be max
        number = 100
        podcasts = []

        # urls to use
        if genre:
            url = "https://itunes.apple.com/us/rss/topaudiopodcasts/limit=" + str(number) + "/genre=" + str(genre.genreid) + "/json"
        else:
            url = "https://itunes.apple.com/us/rss/topaudiopodcasts/limit=" + str(number) + "/json"

        try:
            response = session.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            jsonresponse = response.json()

            # iterate thru every entry, extract podid
            for x in jsonresponse["feed"]["entry"]:
                podid = x["id"]["attributes"]["im:id"]

                if podid:
                    # slow down scraping so as to not get blocked
                    time.sleep(5)
                    Podcast.scrape_podcast(podid)
                    try:
                        podcast = Podcast.objects.get(podid=podid)
                        podcasts.append(podcast)
                    # if podcast don"t exists, scrape it and create it
                    except Podcast.DoesNotExist:
                        pass

        except requests.exceptions.HTTPError:
            logger.error("http error", url)
        except requests.exceptions.ReadTimeout:
            logger.error("timed out", url)
        except requests.exceptions.RetryError:
            logger.error("too many retries:", url)
        return podcasts

    def cache_charts():
        genres = list(Genre.get_primary_genres())
        genres.append(None)

        for provider in ["dopepod", "itunes"]:
            if provider == "dopepod":
                languages = list(Language.get_languages())
                languages.append(None)
            else:
                languages = [None]
            for language in languages:
                for genre in genres:
                    Podcast.search(url="/charts/", provider=provider, genre=genre, language=language, force_cache=True)

class SubscriptionManager(models.Manager):
    def get_queryset(self):
        return super(SubscriptionManager, self).get_queryset().select_related("podcast__genre", "podcast__genre__supergenre", "podcast__language")

class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="subscription")
    podcast = models.ForeignKey(Podcast, on_delete=models.CASCADE, related_name="subscription")
    last_updated = models.DateTimeField(null=True, default=None)
    new_episodes = models.IntegerField(default=0)

    objects = SubscriptionManager()

    class Meta:
        ordering = ("podcast__title",)

    def update(self):
        self.last_updated = timezone.now()
        self.save()

    def get_subscriptions(user):
        subscriptions = Subscription.objects.filter(user=user)
        results = {}
        results["podcasts"] = subscriptions
        results["header"] = "Subscriptions"
        results["view"] = "subscriptions"
        results["subscriptions"] = True
        results["extra_options"] = True
        return results

class EpisodeManager(models.Manager):
    def get_queryset(self):
        return super(EpisodeManager, self).get_queryset().select_related("podcast__genre", "podcast__genre__supergenre", "podcast__language")

class Episode(models.Model):
    podcast = models.ForeignKey(Podcast, on_delete=models.CASCADE, related_name="episode")
    user = models.ForeignKey(User, null=True, default=None, on_delete=models.CASCADE, related_name="episode")
    pubDate = models.DateTimeField(default=None, null=True)
    title = models.CharField(max_length=1000)
    description = models.TextField(max_length=5000, null=True, blank=True)
    length = models.DurationField(null=True, blank=True)
    url = models.CharField(max_length=1000)
    kind = models.CharField(max_length=16)
    size = models.CharField(null=True, blank=True, max_length=16)
    signature = models.CharField(max_length=7000)
    added_at = models.DateTimeField(default=timezone.now)
    played_at = models.DateTimeField(default=None, null=True)
    position = models.IntegerField(default=None, null=True)

    objects = EpisodeManager()

    def get_episodes(url, podid, feedUrl, selected_page=None):
        """
        returns a list of episodes using requests and lxml etree
        """

        f = furl(url)
        f.path = str(f.path).replace("episodes", "showpod")
        f.args["page"] = selected_page
        url = f.url
        results = cache.get(url)

        if results:
            yield results
            return
        else:
            ns = {"itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd",
                "atom": "http://www.w3.org/2005/Atom",
                "im": "http://itunes.apple.com/rss",
            }

            # useragent for requests
            headers = {
                "User-Agent": str(ua.random)
            }

            episodes = []
            flag = False

            results = {
                "episodes": episodes,
            }

            try:
                response = session.get(feedUrl, headers=headers, timeout=5, allow_redirects=True)
                response.raise_for_status()
                try:
                    root = etree.XML(response.content)
                except etree.XMLSyntaxError:
                    logger.error("trouble with xml", feedUrl)
                    try:
                        root = lxml_html.fromstring(response.content) #etree.XML(response.content)
                        root = root.xpath("//rss")[0]
                    except:
                        pass
                        
                ns.update(root.nsmap)
                tree = root.find("channel")

                try:
                    items = tree.findall("item")
                except AttributeError:
                    items = []
                    logger.error("no can do", feedUrl)

                count = len(items)
                page = 1
                i = 1
                show = 50

                num_pages = int(count / show) + (count % show > 0)
                spread = 3

                if selected_page > num_pages:
                    Episode.get_episodes(url, podid, feedUrl, num_pages)
                    
                # TODO sort by pubDate (but how ?!?!?)
                for item in items:
                    episode = {}

                    # try to get pubdate + parse & convert it to datetime
                    try:
                        pubdate = item.find("pubDate").text
                    except AttributeError:
                        # try lowercase
                        try:
                            pubdate = item.find("pubdate").text
                        except AttributeError:
                            pubdate = None
                    try:
                        pubdate = parse(pubdate, default=parse("00:00Z"))
                        # date as a string (used to create signature)
                        episode["date_string"] = datetime.strftime(pubdate,"%b %d %Y %X %z")
                    except (ValueError, TypeError):
                        episode["date_string"] = None

                    # try to get title & description
                    try:
                        episode["title"] = item.find("title").text
                    except AttributeError:
                        try:
                            episode["title"] = item.find("itunes:subtitle").text
                        except AttributeError as e:
                            logger.error("can\'t get title", feedUrl)
                            continue
                    try:
                        description = item.find("description").text
                    except AttributeError:
                        # or try with itunes namespace
                        try:
                            description = item.find("itunes:summary", ns).text
                        # if episode data not found, skip episode
                        except AttributeError as e:
                            description = ""
                            logger.error("can\'t get description", feedUrl)

                    if not description:
                        description = ""
                    else:
                        description = html.unescape(description)

                    # strip html tags+ split + join again by single space
                    episode["description"] = " ".join(strip_tags(description).split())

                    # try to get length
                    try:
                        length = item.find("itunes:duration", ns).text
                    except AttributeError as e:
                        try:
                            length = item.find("duration").text
                        except AttributeError as e:
                            length = None
                            logger.error("can\'t get length", feedUrl)

                    if length:
                        # convert length to timedelta
                        if length.isdigit() and length != 0:
                            delta = timedelta(seconds=int(length))
                            episode["length"] = str(delta)
                        else:
                            if re.search("[1-9]", length):
                                if "." in length:
                                    length = length.split(".")
                                elif ":" in length:
                                    length = length.split(":")

                                try:
                                    hours = int(length[0])
                                    minutes = int(length[1])
                                    seconds = int(length[2])
                                    delta = timedelta(hours=hours, minutes=minutes, seconds=seconds)
                                    episode["length"] = str(delta)
                                except (ValueError, IndexError):
                                    try:
                                        minutes = int(length[0])
                                        seconds = int(length[1])
                                        delta = timedelta(minutes=minutes, seconds=seconds)
                                        episode["length"] = str(delta)
                                    except (ValueError, IndexError):
                                        logger.error("can\'t parse length", feedUrl)

                    episode["podid"] = podid

                    # link to episode
                    # enclosure might be missing, have alternatives
                    enclosure = item.find("enclosure")
                    try:
                        size = enclosure.get("length")
                        if size and int(size) > 100:
                            episode["size"] = format_bytes(int(size))
                    except (AttributeError, ValueError):
                        logger.error("can\'t get episode size", feedUrl)

                    try:
                        episode["url"] = enclosure.get("url").replace("http:", "")
                        episode["type"] = enclosure.get("type")

                        # create signature
                        episode["signature"] = signing.dumps(episode)
                        # datetime date
                        episode["pubDate"] = pubdate
                        episode["position"] = count - i + 1

                        episodes.append(episode)

                        if count < show:
                            pass
                        elif i % show == 0:
                            # paginate
                            if num_pages > 1:
                                pages = range((page - spread if page - spread > 1 else 1),
                                            (page + spread if page + spread <= num_pages else num_pages) + 1)
                                pages_urls = []

                                for p in pages:
                                    if p == page:
                                        pages_urls.append(None)
                                    else:
                                        f = furl(url)
                                        f.args["page"] = p
                                        pages_urls.append(f.url)
                                #  zip pages & use list to make it reusable
                                results["pages"] = list(zip(pages, pages_urls))

                                if page < num_pages - spread:
                                    f = furl(url)
                                    f.args["page"] = num_pages
                                    results["end_url"] = f.url
                                else:
                                    results["end_url"] = None
                                
                                if page > 1 + spread:
                                    f = furl(url)
                                    del f.args["page"]
                                    results["start_url"] = f.url
                                else:
                                    results["start_url"] = None
                            
                            f = furl(url)
                            f.args["page"] = page
                            url = f.url
                            results.update({
                                "episodes": episodes,
                            })
                            cache.set(url, copy.deepcopy(results), 60 * 60 * 24)
                            if page == selected_page:
                                flag = True
                                yield copy.deepcopy(results)
                            del episodes[:]
                            page += 1
                        i += 1
                    except AttributeError as e:
                        logger.error("can\'t get episode url/type/size", feedUrl)

            except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError, requests.exceptions.InvalidSchema, requests.exceptions.MissingSchema):
                logger.error("connection error", feedUrl)

            if episodes:
                # paginate
                if num_pages > 1:
                    pages = range((page - spread if page - spread > 1 else 1),
                                    (page + spread if page + spread <= num_pages else num_pages) + 1)
                    pages_urls = []

                    for p in pages:
                        if p == page:
                            pages_urls.append(None)
                        else:
                            f = furl(url)
                            f.args["page"] = p
                            pages_urls.append(f.url)
                    #  zip pages & use list to make it reusable
                    results["pages"] = list(
                        zip(pages, pages_urls))

                    if page < num_pages - spread:
                        f = furl(url)
                        f.args["page"] = num_pages
                        results["end_url"] = f.url
                    else:
                        results["end_url"] = None

                    if page > 1 + spread:
                        f = furl(url)
                        del f.args["page"]
                        results["start_url"] = f.url
                    else:
                        results["start_url"] = None

                f = furl(url)
                f.args["page"] = page
                url = f.url

                results.update({
                    "episodes": episodes,
                })
                cache.set(url, copy.deepcopy(results), 60 * 60 * 24)
            else:
                print(feedUrl)
            if flag:
                return
            else:
                yield results
                
    def set_new(user, podid, episodes):
        if user.is_authenticated:
            try:
                subscription = Subscription.objects.get(user=user, podcast__podid=podid)
                i = 0
                # iterate thru episodes till episode pubDate is older than last_updated
                for episode in episodes:
                    if episode["pubDate"]:
                        if not subscription.last_updated or subscription.last_updated < episode["pubDate"]:
                            i += 1
                            episode["is_new"] = True
                        else:
                            break

                subscription.last_updated = timezone.now()
                subscription.new_episodes = i
                subscription.save()
            except Subscription.DoesNotExist:
                pass
        return episodes

    def played_ago(self):
        if self.played_at:
            ago = timezone.now() - self.played_at
            seconds = ago.total_seconds()
            days = int(seconds // (60 * 60 * 24))
            hours = int((seconds % (60 * 60 * 24)) // (60 * 60))
            minutes = int((seconds % (60 * 60)) // 60)
            seconds = int(seconds % 60)
            ago = ""
            if days:
                ago += str(days) + "d "
            if hours:
                ago += str(hours) + "h "
            if minutes:
                ago += str(minutes) + "m "
            if seconds:
                ago += str(seconds) + "s "
            ago += " ago"
            if ago[0] == " ":
                ago = "0s ago"
            return ago

    def get_last_played():
        """ 
        returns all last played episodes
        """

        results = cache.get("last_played")
        if results:
            return results
        else:
            last_played = Episode.objects.filter(position=None).order_by("-played_at",)
            results = {}
            results["episodes"] = last_played
            results["header"] = "Last played"
            results["view"] = "last_played"
            cache.set("last_played", results, 60 * 60 * 24)
            return results

    def play(self):
        episodes = Episode.objects.filter(user=self.user).order_by("position")
        try:
            for episode in episodes[self.position:]:
                episode.position = F("position") - 1
                episode.save()
        except (IndexError, AssertionError):
            return

        self.podcast.plays = F("plays") + 1
        self.podcast.save()
        self.played_at = timezone.now()
        self.position = None
        self.user = None
        self.save()

        # if played is same as previous, delete previous
        # if list is longer than 50, delete excess
        with transaction.atomic():
            last_played = Episode.objects.select_related(None).select_for_update().filter(position=None).order_by("-played_at")
            if last_played.count() > 1:
                if last_played[0].signature == last_played[1].signature:
                    last_played[1].delete()
                if last_played.count() > 50:
                    excess = last_played[49:last_played.count() - 1]
                    for episode in excess:
                        episode.delete()

        # let's cache those bad boys
        last_played = Episode.objects.filter(position=None).order_by("-played_at")
        results = {}
        results["episodes"] = last_played
        results["header"] = "Last played"
        results["view"] = "last_played"
        cache.set("last_played", results, 60 * 60 * 24)

    def add(signature, user):
        # max 20 episodes for now
        if user.is_authenticated:
            # get position of last episode
            position = Episode.objects.filter(user=user).aggregate(Max("position"))["position__max"]
            if position:
                if position == 20:
                    user = None
                    position = None
                else:
                    position += 1
            else:
                position = 1
        else:
            user = None
            position = None

        try:
            data = signing.loads(signature)
            podid = data["podid"]
            podcast = Podcast.objects.get(podid=podid)
            url = data["url"]
            kind = data["type"]
            title = data["title"]
            description = data["description"]
        except (KeyError, ValueError, Podcast.DoesNotExist, signing.BadSignature):
            return
        
        try:
            pubDate = datetime.strptime(data["date_string"],"%b %d %Y %X %z")
        except:
            pubDate = None

        try:
            length = data["length"]
            t = datetime.strptime(length,"%H:%M:%S")
            length = timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)
        except (KeyError, ValueError):
            length = None

        try:
            size = data["size"]
        except KeyError:
            size = None
            
        return Episode.objects.create(
            user=user,
            url=url,
            kind=kind,
            title=title,
            pubDate=pubDate,
            podcast=podcast,
            length=length,
            size=size,
            description=description,
            signature=signature,
            position=position,
        )

    def remove(pos, user):
        episodes = Episode.objects.filter(user=user).order_by("position")
        try:
            episodes[pos - 1].delete()
            for episode in episodes[pos - 1:]:
                episode.position -= 1
                episode.save()
        except (IndexError, AssertionError):
            return

    def up(pos, user):
        episodes = Episode.objects.filter(user=user).order_by("position")
        try:
            episode1 = episodes[pos - 1 - 1]
            episode2 = episodes[pos - 1]
            episode1.position += 1
            episode2.position -= 1
            episode1.save()
            episode2.save()
        except (IndexError, AssertionError):
            return

    def down(pos, user):
        episodes = Episode.objects.filter(user=user).order_by("position")
        try:
            episode1 = episodes[pos - 1]
            episode2 = episodes[pos]
            episode1.position += 1
            episode2.position -= 1
            episode1.save()
            episode2.save()
        except (IndexError, AssertionError):
            return

    def get_playlist(user):
        episodes = Episode.objects.filter(user=user).order_by("position")

        results = {}
        results["episodes"] = episodes
        results["header"] = "Playlist"
        results["view"] = "playlist"
        results["extra_options"] = True
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

        languages = Language.get_languages()
        for language in languages:
            language.n_podcasts = Podcast.objects.filter(language=language).count()
            language.save()

class GenreManager(models.Manager):
    def get_queryset(self):
        return super(GenreManager, self).get_queryset().select_related("supergenre")

class Genre(Filterable):
    genreid = models.IntegerField()
    supergenre = models.ForeignKey("podcasts.Genre", on_delete=models.CASCADE, blank=True, null=True)

    objects = GenreManager()

    class Meta:
        ordering = ("name",)

    def get_primary_genres():
        """
        returns primary genres
        """
        results = cache.get("genres")
        if results:
            return results
        else:
            results = Genre.objects.filter(supergenre=None)
            cache.set("genres", results, 60 * 60 * 24)
            return results 

class Language(Filterable):
    
    class Meta:
        ordering = ("-n_podcasts",)

    def get_languages():
        """
        returns languages
        """
        results = cache.get("languages")
        if results:
            return results
        else:
            results = Language.objects.all()
            cache.set("languages", results, 60 * 60 * 24)
            return results 

# class SearchTerm(models.Model):
#     number = models.IntegerField()
#     text = models.CharField(max_length=100)
#
#     class Meta:
#         ordering = ("number",)
