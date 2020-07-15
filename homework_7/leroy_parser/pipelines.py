# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.pipelines.images import ImagesPipeline

import scrapy
from pymongo import MongoClient


class DataBasePipeline:
    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.mongo_base = self.client.construction_products

    # В базу почему-то ничего не пишется. Почему, абсолютно не ясно :(
    def process_item(self, item, spider):
        collection = self.mongo_base[spider.name]
        collection.insert_one(item)
        return item

    def __del__(self):
        self.client.close()


class LeroyPhotosPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['photos']:
            for img in item['photos']:
                try:
                    yield scrapy.Request(img, meta=item)
                except Exception as e:
                    print(e)

    def file_path(self, request, response=None, info=None):
        item = request.meta
        return f'full/{item["name"]}/{item["photos"].index(request.url)}.jpg'

    def item_completed(self, results, item, info):
        if results:
            item['photos'] = [itm[1] for itm in results if itm[0]]

        # Заполнение словаря свойств из двух списков: списка свойств и списка значений.
        # Вообще, делать это нужно не здесь :) но где еще, не придумал. Наверное, нужно написать отдельный pipeline.
        # Получилось опасно, алгоритм ожидает, что количество свойств всегда будет равно количеству значений.
        # По-хорошему заполнять словарь еще при парсинге страницы (разобраться, если будет время).
        item['properties'] = {}
        for i in range(len(item['props_list'])):
            prop = item['props_list'][i]
            prop_val = item['props_val_list'][i]
            item['properties'][prop] = prop_val

        # Удаление ставших ненужными списков
        item.pop('props_list', None)
        item.pop('props_val_list', None)

        return item
