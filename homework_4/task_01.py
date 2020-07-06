# 1)Написать приложение, которое собирает основные новости с сайтов news.mail.ru, lenta.ru, yandex.news
# Для парсинга использовать xpath. Структура данных должна содержать:
# название источника,
# наименование новости,
# ссылку на новость,
# дата публикации
#
# 2)Сложить все новости в БД

from pprint import pprint
from lxml import html
import requests
from datetime import date
from pymongo import MongoClient
from pymongo import errors

header = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'}

# Параметры работы с БД
client = MongoClient('localhost', 27017)
db = client['news_db']


def save_new_to_db(new):
    # функция записи в БД. Возвращает 1, если вакансия была добавлена, и 0, если нет (уже есть в базе)
    try:
        db.news.insert_one(new)
    except errors.DuplicateKeyError:
        pass
        return 0
    else:
        return 1


def request_to_yandex():
    # функция для сбора новостей из Яндекса
    base_url = 'https://yandex.ru/news'
    response = requests.get(base_url, headers=header)

    dom = html.fromstring(response.text)

    items = dom.xpath(
        "//div[@class='stories-set stories-set_main_no stories-set_pos_1']//td[@class='stories-set__item']")

    for item in items:
        new = {}
        name = item.xpath(".//a/text()")
        url = item.xpath(".//a/@href")
        source = item.xpath(".//div[@class='story__date']/text()")
        new['source'] = ' '.join(source[0].split(' ')[:-1])
        time = source[0].split(' ')[-1]
        new['time'] = f'{date.today()} {time}'
        new['name'] = name[0].replace(u'\n', u'')
        new['url'] = base_url + url[0]
        save_new_to_db(new)


def request_to_lenta():
    # функция для сбора новостей из Ленты
    base_url = 'https://lenta.ru'
    response = requests.get(base_url, headers=header)

    dom = html.fromstring(response.text)

    items = dom.xpath(
        "//div[@class='span8 js-main__content']//div[@class='span4']/div[@class='item']")

    for item in items:
        new = {}
        name = item.xpath(".//a/text()")
        url = item.xpath(".//a/@href")
        time = item.xpath(".//time/text()")
        new['source'] = 'lenta.ru'
        new['time'] = f'{date.today()} {time[0]}'
        new['name'] = name[0].replace(u'\xa0', u' ')
        new['url'] = base_url + url[0]
        save_new_to_db(new)


def request_to_mail():
    # функция для сбора новостей из Mail
    base_url = 'https://news.mail.ru'
    response = requests.get(base_url, headers=header)

    dom = html.fromstring(response.text)

    items = dom.xpath(
        "//div[@class='block block_bg_primary block_separated_top link-hdr']//span//a")

    for item in items:
        new = {}
        name = item.xpath(".//span/text()")
        url = item.xpath("./@href")[0]

        # Переход по новости для подробной информации
        new_more = requests.get(url, headers=header)
        dom_more = html.fromstring(new_more.text)
        time = dom_more.xpath("//span[@class='note__text breadcrumbs__text js-ago']/text()")[0]
        source = dom_more.xpath("//a[@class='link color_gray breadcrumbs__link']/span/text()")

        new['source'] = source[0]
        new['time'] = time if time.find(':') == -1 else f'{date.today()} {time}'
        new['name'] = name[0].replace(u'\xa0', u' ')
        new['url'] = url
        save_new_to_db(new)


request_to_yandex()
request_to_lenta()
request_to_mail()
