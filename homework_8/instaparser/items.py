# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class InstaparserItem(scrapy.Item):
    # define the fields for your item here like:
    user_id = scrapy.Field()
    _id = scrapy.Field()

    subscription_id = scrapy.Field()
    subscription_photo = scrapy.Field()
    subscription_name = scrapy.Field()
    subscription = scrapy.Field()

    subscriber_id = scrapy.Field()
    subscriber_photo = scrapy.Field()
    subscriber_name = scrapy.Field()
    subscriber = scrapy.Field()
