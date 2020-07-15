from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from leroy_parser.spiders.leroy import LeroySpider
from leroy_parser import settings


if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(LeroySpider,search_string='Шуруповерт')

    process.start()
