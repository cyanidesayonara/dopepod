import scrapy
from podcasts.models import Genre, Podcast

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
            genreid = genre.xpath('a/@href').re_first(r'/id(\d+)')
            supergenre, created = Genre.objects.select_related(None).select_for_update().update_or_create(
                name=supergenre,
                genreid=genreid,
                supergenre=None,
            )
            for subgenre in genre.xpath('ul/li'):
                name = subgenre.xpath('a/text()').extract_first()
                genreid = subgenre.xpath('a/@href').re_first(r'/id(\d+)')
                Genre.objects.select_related(None).select_for_update().update_or_create(
                    name=name,
                    genreid=genreid,
                    supergenre=supergenre,
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
        gets podid from podcast link
        lookups podcast by podid
        """

        for link in response.xpath('//div[@id="selectedcontent"]/div/ul/li/a[contains(@href, "id")]'):
            podid = link.xpath('@href').re_first(r'/id(\w+)')
            Podcast.scrape_podcast(podid)
