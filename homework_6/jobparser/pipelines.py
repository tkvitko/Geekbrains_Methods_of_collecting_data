# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient
import re


class JobparserPipeline:
    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.mongo_base = self.client.vacansy124

    def process_item(self, item, spider):
        collection = self.mongo_base[spider.name]
        salary = ''.join(item['salary'])
        item['salary_min'], item['salary_max'], item['currency'] = self.process_salary(salary)
        del item['salary']
        collection.insert_one(item)

        return item

    def __del__(self):
        self.client.close()

    def process_salary(self, salary_string):
        # функция для разбиения строки с зарплатой на подстроки (от, до, валюта)
        salary_string = re.sub('(?<=\d)\s(?=\d)', '', salary_string)  # уберем пробелымежду цифрами (внцри чисел)
        salary_string = salary_string.lower()
        words = re.findall(r'\w+', salary_string)  # составим список слов из строки

        salary_from, salary_to, salary_currency = None, None, None

        if words:
            if len(words) > 2:
                if words[2] != 'не':
                    salary_currency = words[2]

            if words.count('от') != 0:
                salary_from = words[1]
            elif words.count('до') != 0:
                salary_to = words[1]
            elif words.count('по') != 0:
                pass
            elif words.count('не') != 0:
                pass
            else:
                salary_from = words[0]
                salary_to = words[1]

        return salary_from, salary_to, salary_currency
