import scrapy
from scrapy.http import HtmlResponse
from leroy_parser.items import LeroyparserItem
from scrapy.loader import ItemLoader


class LeroySpider(scrapy.Spider):
    name = 'leroy'
    allowed_domains = ['leroymerlin.ru']

    def __init__(self, search_string):
        self.start_urls = [f'https://leroymerlin.ru/search/?q={search_string}']

    def parse(self, response):
        product_links = response.xpath("//a[@class='black-link product-name-inner']")
        for link in product_links:
            yield response.follow(link, callback=self.parse_products)

    def parse_products(self, response: HtmlResponse):
        loader = ItemLoader(item=LeroyparserItem(), response=response)
        loader.add_xpath('name', "//h1/text()")
        loader.add_xpath('photos', "//picture[@slot='pictures']/img/@src")
        loader.add_xpath('price', "//span[@slot='price']/text()")
        loader.add_value('url', response.url)
        loader.add_xpath('props_list', "//div[@class='def-list__group']/dt/text()")
        loader.add_xpath('props_val_list', "//div[@class='def-list__group']/dd/text()")
        yield loader.load_item()
