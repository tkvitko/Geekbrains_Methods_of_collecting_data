# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst


def list_to_int(value):
    return int(value.replace(' ', ''))


def clear_spaces(value):
    return value.replace('\n', '').replace(' ', '')


class LeroyparserItem(scrapy.Item):
    # define the fields for your item here like:

    _id = scrapy.Field()
    name = scrapy.Field(output_processor=TakeFirst())
    photos = scrapy.Field()
    price = scrapy.Field(input_processor=MapCompose(list_to_int), output_processor=TakeFirst())
    url = scrapy.Field(output_processor=TakeFirst())
    props_list = scrapy.Field()
    props_val_list = scrapy.Field(input_processor=MapCompose(clear_spaces))
    properties = scrapy.Field()
