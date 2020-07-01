# 2) Написать функцию, которая производит поиск и выводит на экран вакансии с заработной платой больше введенной суммы.
# Поиск по двум полям (мин и макс зарплату)

from pymongo import MongoClient
from pprint import pprint

client = MongoClient('localhost', 27017)
db = client['vacancies_db_test']
collection = db.vacancies


def print_vacs(salary):
    for vac in db.vacancies.find({'$or': [{'salary_from': {'$gt': salary}}, {'salary_to': {'$gt': salary}}]}):
        pprint(vac)


sum = int(input('Вывести вакансии с зарплатой выше (рублей): '))
print_vacs(sum)
