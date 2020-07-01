# Необходимо собрать информацию о вакансиях на вводимую должность (используем input или через аргументы) с сайта superjob.ru и hh.ru.
# Приложение должно анализировать несколько страниц сайта(также вводим через input или аргументы).
# Получившийся список должен содержать в себе минимум:
#     *Наименование вакансии
#     *Предлагаемую зарплату (отдельно мин. и отдельно макс. и отдельно валюта)
#     *Ссылку на саму вакансию
#     *Сайт откуда собрана вакансия
# По своему желанию можно добавить еще работодателя и расположение.
# Данная структура должна быть одинаковая для вакансий с обоих сайтов.
# Общий результат можно вывести с помощью dataFrame через pandas.

import requests
from pprint import pprint
import re  # потребуется для разбора строки регулярным выражением
from bs4 import BeautifulSoup as bs
from pymongo import MongoClient
from pymongo import errors


def salary_parser(salary_string):
    # функция для разбиения строки с зарплатой на подстроки (от, до, валюта)
    salary_string = re.sub('(?<=\d)\s(?=\d)', '', salary_string)  # уберем пробелымежду цифрами (внцри чисел)
    salary_string = salary_string.lower()
    words = re.findall(r'\w+', salary_string)  # составим список слов из строки

    salary_from, salary_to, salary_currency = None, None, None

    if words:
        if len(words) == 2:
            if words.count('по') != 0:
                pass
            else:
                salary_currency = words[1]
                salary_from = int(words[0])
        elif len(words) == 3:
            salary_currency = words[2]
            if words.count('от') != 0:
                salary_from = int(words[1])
            elif words.count('до') != 0:
                salary_to = int(words[1])
            else:
                salary_from = int(words[0])
                salary_to = int(words[1])

    return salary_from, salary_to, salary_currency


def save_vacancy_to_db(vacancy_data):
    # функция записи в БД. Возвращает 1, если вакансия была добавлена, и 0, если нет (уже есть в базе)
    try:
        db.vacancies.insert_one(vacancy_data)
    except errors.DuplicateKeyError:
        pass
        return 0
    else:
        return 1


# Параметры работы с БД
client = MongoClient('localhost', 27017)
db = client['vacancies_db_test']

# Ввод данных и хедер для запросов
search_string = input('Строка для поиска: ')
header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36',
    'Accept': '*/*'}

new_vac_count = 0

# Работа с hh.ru
main_link = 'https://spb.hh.ru'
url = f'{main_link}/search/vacancy?clusters=true&enable_snippets=true&text={search_string}&L_save_area=true&area=113&from=cluster_area&showClusters=false'

next_page_exists = True
pages_hh = 0

while next_page_exists:

    response = requests.get(url, headers=header).text
    soup = bs(response, "lxml")

    vacancies_block = soup.find('div', {'class': 'vacancy-serp'})
    vacancies_list = vacancies_block.find_all('div', {'class': 'vacancy-serp-item'})

    for vacancy in vacancies_list:
        vacancy_data = {}
        vacancy_data['name'] = vacancy.find('span', {'class': 'g-user-content'}).getText()
        vacancy_data['url'] = vacancy.find('a', {'class': 'bloko-link HH-LinkModifier'})['href']
        vacancy_data['_id'] = 'hh_' + vacancy_data['url'].split('?')[0].split('/')[4]
        vacancy_data['source'] = 'hh.ru'
        vacancy_data['employer'] = vacancy.find('div', {'class': 'vacancy-serp-item__meta-info'}).getText().replace(
            u'\xa0',
            u'')
        vacancy_data['city'] = vacancy.find('span', {'class': 'vacancy-serp-item__meta-info'}).getText()
        salary_string = vacancy.find('div', {'class': 'vacancy-serp-item__sidebar'}).getText().replace(u'\xa0', u'')
        vacancy_data['salary_string'] = salary_string
        vacancy_data['salary_from'], vacancy_data['salary_to'], vacancy_data['salary_currency'] = salary_parser(
            salary_string)

        new_vac_count += save_vacancy_to_db(vacancy_data)

    pages_hh += 1
    next_page_block = soup.find('a', {'class': 'HH-Pager-Controls-Next'})
    if next_page_block:
        next_page_exists = True
        next_page_url = next_page_block['href']
        url = f'{main_link}{next_page_url}'
    else:
        next_page_exists = False

print(f'{pages_hh} страниц(ы) hh.ru обработано')

# Работа с superjob.ru

main_link = 'https://russia.superjob.ru'
url = f'{main_link}/vacancy/search/?keywords={search_string}'

next_page_exists = True
pages_sj = 0

while next_page_exists:

    response = requests.get(url, headers=header).text
    soup = bs(response, "lxml")

    vacancies_block = soup.find('div', {'class': '_1ID8B'})
    vacancies_list = vacancies_block.find_all('div', {'class': 'f-test-vacancy-item'})

    for vacancy in vacancies_list:
        vacancy_data = {}
        name_block = vacancy.find('a', {'class': 'icMQ_'})
        if name_block:
            vacancy_data['name'] = name_block.getText()
        url_block = vacancy.find('a', {'class': 'icMQ_'})
        if url_block:
            vacancy_data['url'] = main_link + url_block['href']
            vacancy_data['source'] = 'superjob.ru'
            vacancy_data['_id'] = 'sj_' + vacancy_data['url'].split('-')[-1].split('.')[0]
        employer_block = vacancy.find('span', {'class': 'f-test-text-vacancy-item-company-name'})
        if employer_block:
            vacancy_data['employer'] = employer_block.getText().replace(u'\xa0', u'')
        city_block = vacancy.find('span', {'class': 'f-test-text-company-item-location'})
        if city_block:
            vacancy_data['city'] = city_block.findChildren(resurcive=False)[2].getText()
        salary_block = vacancy.find('span', {'class': '_3mfro'})
        if salary_block:
            salary_string = salary_block.getText().replace(u'\xa0', u' ')
            vacancy_data['salary_string'] = salary_string
            vacancy_data['salary_from'], vacancy_data['salary_to'], vacancy_data['salary_currency'] = salary_parser(
                salary_string)

        new_vac_count += save_vacancy_to_db(vacancy_data)

    pages_sj += 1

    next_page_block = soup.find('a', {'class': 'f-test-link-Dalshe'})
    if next_page_block:
        next_page_exists = True
        next_page_url = next_page_block['href']
        url = f'{main_link}{next_page_url}'
    else:
        next_page_exists = False

print(f'{pages_sj} страниц(ы) superjob.ru обработано')
print(f'{new_vac_count} новых вакансий добавлено')
