import scrapy
import json
import requests
import sys
from willy.items import PodcastItem, GenreItem
from datetime import datetime

class WillyTheSpider(scrapy.Spider):
    name = 'willy'
    allowed_domains = ['itunes.apple.com']
    start_urls = [
        'https://itunes.apple.com/us/genre/podcasts/id26',
    ]

    def parse(self, response):
        """
        parses genre data, yield genre items
        follows each genre link
        parses podcasts on main page
        follows links to each alphabet
        """

        for genre in response.xpath('//div[@id="genre-nav"]/div[@class="grid3-column"]/ul/li'):
            supergenre = genre.xpath('a/text()').extract_first()
            itunesid = genre.xpath('a/@href').re_first(r'/id(\d+)')
            yield GenreItem (
                name=supergenre,
                itunesid=itunesid,
                n_podcasts=0,
                supergenre=None,
            )
            for subgenre in genre.xpath('ul/li'):
                name = subgenre.xpath('a/text()').extract_first()
                itunesid = subgenre.xpath('a/@href').re_first(r'/id(\d+)')
                yield GenreItem (
                    name=name,
                    n_podcasts=0,
                    supergenre=supergenre,
                    itunesid=itunesid,
                )

        for link in response.xpath('//div[@id="genre-nav"]/div/ul/li/a'):
            url = link.xpath('@href').extract_first().split('?')[0]
            yield scrapy.Request(url, meta = {
                      'dont_redirect': True,
                  }, callback=self.parse_podcasts, dont_filter=True)

        for link in response.xpath('//div[@id="genre-nav"]/div/ul/li/a'):
            url = link.xpath('@href').extract_first().split('?')[0]
            yield scrapy.Request(url, meta = {
                      'dont_redirect': True,
                  }, callback=self.parse_abc, dont_filter=True)

        for link in response.xpath('//div[@id="genre-nav"]/div/ul/li/ul/li/a'):
            url = link.xpath('@href').extract_first().split('?')[0]
            yield scrapy.Request(url, meta = {
                      'dont_redirect': True,
                  }, callback=self.parse_podcasts, dont_filter=True)

        for link in response.xpath('//div[@id="genre-nav"]/div/ul/li/ul/li/a'):
            url = link.xpath('@href').extract_first().split('?')[0]
            yield scrapy.Request(url, meta = {
                      'dont_redirect': True,
                  }, callback=self.parse_abc, dont_filter=True)

    def parse_abc(self, response):
        """
        follows links to each pagination
        """

        for link in response.xpath('//div[@id="selectedgenre"]/ul/li/a'):
            url = response.url + '?' + link.xpath('@href').extract_first().split('&')[-1]
            yield scrapy.Request(url, meta = {
                      'dont_redirect': True,
                  }, callback=self.parse_pagination)

    def parse_pagination(self, response):
        """
        parses all podcasts on each page
        """

        for link in response.xpath('//div[@id="selectedgenre"]/ul[2]/li/a'):
            url = response.url + '&' + link.xpath('@href').extract_first().split('&')[-1].replace('#page', '')
            yield scrapy.Request(url, meta = {
                      'dont_redirect': True,
                  }, callback=self.parse_podcasts)

    def parse_podcasts(self, response):
        """
        gets itunesid from podcast link
        lookups podcast by itunesid
        """

        for link in response.xpath('//div[@id="selectedcontent"]/div/ul/li/a[contains(@href, "id")]'):
            itunesid = link.xpath('@href').re_first(r'/id(\w+)')
            url = 'https://itunes.apple.com/lookup?id=' + itunesid
            yield scrapy.Request(url, meta = {
                      'dont_redirect': True,
                  }, callback=self.parse_lookup)

    def parse_lookup(self, response):
        """
        saves lookup data to request meta
        follows itunesUrl to artist page
        """

        jsonresponse = json.loads(response.body_as_unicode())
        data = jsonresponse['results'][0]

        itunesUrl = data['collectionViewUrl'].split('?')[0]
        request = scrapy.Request(itunesUrl, meta = {
                  'dont_redirect': True,
              }, callback=self.parse_itunesurl)
        request.meta['data'] = data
        yield request

    def parse_itunesurl(self, response):
        """
        scrapes data from artist page
        unpacks lookup data
        returns podcast item (if all data is present)
        """

        description = response.xpath('//div[@class="product-review"]/p/text()').extract_first()
        language = response.xpath('//li[@class="language"]/text()').extract_first()
        copyrighttext = response.xpath('//li[@class="copyright"]/text()').extract_first()
        podcastUrl = response.xpath('//div[@class="extra-list"]/ul[@class="list"]/li/a/@href').extract_first()

        if not copyrighttext:
            copyrighttext = '© All rights reserved'

        if not description:
            description = ''

        try:
            data = response.meta['data']
            itunesid = data['collectionId']
            feedUrl = data['feedUrl']
            title = data['collectionName']
            artist = data['artistName']
            artworkUrl = data['artworkUrl600'].replace('600x600bb.jpg', '')[7:]
            genre = data['primaryGenreName']
            explicit = True if data['collectionExplicitness'] == 'explicit' else False
            reviewsUrl = 'https://itunes.apple.com/us/rss/customerreviews/id=' + str(itunesid) + '/xml'

            # useragent headers for requests
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'
            }

            try:
                # make sure feedUrl works
                response = requests.get(feedUrl, headers=headers, timeout=30)
                response.raise_for_status()

                return PodcastItem (
                    itunesid=itunesid,
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

            except requests.exceptions.HTTPError:
                with open('logs.txt', 'a', encoding='utf-8') as f:
                    f.write(str(datetime.now()) + ' | No response from feedUrl' + ' -- ' + str(data) + '\n\n')

            except requests.exceptions.ReadTimeout as e:
                with open('logs.txt', 'a', encoding='utf-8') as f:
                    f.write(str(datetime.now()) + ' | feedUrl timed out' + ' -- ' + str(data) + '\n\n')

        except KeyError as e:
            print('Missing data: ' + str(e))
            with open('logs.txt', 'a', encoding='utf-8') as f:
                f.write(str(datetime.now()) + ' | Missing data: ' + str(e) + ' -- ' + str(data) + '\n\n')
