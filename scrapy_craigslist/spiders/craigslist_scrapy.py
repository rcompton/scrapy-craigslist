__author__ = 'rycpt'

from scrapy.linkextractors import LinkExtractor
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.spiders import Rule, CrawlSpider
from scrapy.selector import Selector
from scrapy_craigslist.items import ScrapyCraigslistItem
from scrapy.http import Request
from urlparse import urljoin
from urlparse import urlparse
import time
import random

def extract_domain(url):
    parsed_uri = urlparse(url)
    return '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)

class CraigslistSpider(CrawlSpider):
    name = 'craigslist'

    def __init__(self, topic='rid'):
        self.topic = topic
        with open('craiglists.csv','r') as fin:
            city_pages = set([line.strip() for line in fin])
        city_pages = list(city_pages)
        random.shuffle(city_pages)
        self.start_urls = [urljoin(x,'/search/{}?'.format(topic)) for x in city_pages]
        self.allowed_domains = [extract_domain(x) for x in self.start_urls]
        super(CraigslistSpider, self).__init__()

    def start_requests(self):
        for url in self.start_urls:
            print url
            yield Request(url, callback=self.parse_search_results)
            ts = random.randint(5, 30)
            print 'sleep for {}...'.format(ts)
            time.sleep(ts)

    def parse_search_results(self, response):
        """
        Parse the urls and titles from the search results
        """
        items = []
        hxs = Selector(response)
        domain = extract_domain(response.url)
        contents = hxs.xpath("//div[@class='content']/*")
        contents2 = hxs.xpath("//div[@class='content']/*/*")
        contents = contents + contents2
        #from scrapy.shell import inspect_response
        #inspect_response(response, self)
        for content in contents:
            try:
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
            except:
                print "problem, eh"
        return items
