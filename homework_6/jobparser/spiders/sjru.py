import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem


class SjruSpider(scrapy.Spider):
    name = 'sjru'
    allowed_domains = ['superjob.ru']
    start_urls = ['https://russia.superjob.ru/vacancy/search/?keywords=python']

    def parse(self, response: HtmlResponse):
        next_page = response.css('a.f-test-link-Dalshe::attr(href)').extract_first()

        vacansy_links = response.xpath(
            "//div[@class='_3zucV _1fMKr undefined _1NAsu']//div[@class='jNMYr GPKTZ _1tH7S']//a/@href").extract()
        for link in vacansy_links:
            yield response.follow(link, callback=self.vacansy_parse)

        yield response.follow(next_page, callback=self.parse)

    def vacansy_parse(self, response: HtmlResponse):
        name_vac = response.css('h1::text').extract_first()
        salary_vac = response.xpath("//span[@class='_3mfro _2Wp8I PlM3e _2JVkc']/text()").extract()
        url_vac = response.url
        source_vac = 'superjob.ru'

        yield JobparserItem(name=name_vac, salary=salary_vac, url=url_vac, source=source_vac)
