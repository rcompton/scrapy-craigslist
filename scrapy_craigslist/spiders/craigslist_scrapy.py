__author__ = 'htm'

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
    """
    This CrawlSpider will look into the specific city and pull out content for
    Title, Ad's URL, Post Date, Post Date Specific (i.e. datetime), Price,
    Room Details, and Locations. Please reference https://sites.google.com/site/clsiteinfo/city-site-code-sort
    for more on city codes and link.

    If you need to change the city code, please do so at the three locations below:
    allowed domains, start urls, and rules.

    Feel free to change the name of the spider to something more specific.

    """
    name = 'craigslist'

    def __init__(self, city='sfbay', topic='rid'):
        self.allowed_domains = ['{}.craigslist.org'.format(city)]
        self.topic = topic
        self.city = city
        self.start_urls = ['http://{0}.craigslist.org/search/{1}?'.format(city, topic)]
        # self.rules = (
        #     Rule(LxmlLinkExtractor(
        #         allow=(r'{0}.craigslist.org/.*/{1}/.*'.format(city, topic)),
        #         # allow=(r'.*/search/apa\?s\=\d+.*'),
        #         deny = (r'.*format\=rss.*')
        #     ),
        #         callback="parse_items_1",
        #         follow= False,
        #          ),
        #     )
        super(CraigslistSpider, self).__init__()

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url, callback=self.parse_items_1)

    def parse_items_1(self, response):
        """
        This function takes teh content from contents and map them according to the
        items from items.py. If the key exists in content, then Scrapy will aggregate
        the rest of the items and combine them.

        Each content will have "[0]" to indicate the first listing from the array.
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
