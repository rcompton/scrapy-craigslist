__author__ = 'rycpt'

from scrapy.linkextractors import LinkExtractor
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.spiders import Rule, CrawlSpider
from scrapy.selector import Selector
from scrapy_craigslist.items import ScrapyCraigslistItem
from scrapy.http import Request
from urlparse import urljoin
from urlparse import urlparse

DOWNLOAD_DELAY = 0.5    # craig blocks you fast

class CraigslistSpider(CrawlSpider):
    name = 'craigslist'

    def __init__(self, city='sfbay', topic='rid'):
        self.allowed_domains = ['{}.craigslist.org'.format(city)]
        self.topic = topic
        self.city = city
        self.start_urls = ['http://{0}.craigslist.org/search/{1}?'.format(city, topic)]
        super(CraigslistSpider, self).__init__()

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url, callback=self.parse_items_1)

    def parse_search_results(self, response):
        """
        Parse the urls and titles from the search results
        """
        items = []
        hxs = Selector(response)
        parsed_uri = urlparse(response.url)
        domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
        contents = hxs.xpath("//div[@class='content']/*")
        for content in contents:
            item = ScrapyCraigslistItem()
            title = content.xpath(".//*[@class='hdrlnk']/text()").extract()
            if title:
                item['title'] = title[0]
            ad_relative_url = content.xpath(".//*[@class='hdrlnk']/@href").extract()
            if ad_relative_url:
                item['ad_url'] = urljoin(domain, ad_relative_url[0])
            post_date = content.xpath(".//*[@class='pl']/time/@datetime").extract()
            if post_date:
                item['post_date'] = post_date[0]
            location = content.xpath(".//*[@class='l2']/*[@class='pnr']/small/text()").extract()
            if location:
                item['location'] = location[0].strip().strip('(').strip(')')
            # print ('**parse-items_1:', item["title"])
            items.append(item)
        return items
