import re

def salary_parser(salary_string):
    # функция для разбиения строки с зарплатой на подстроки (от, до, валюта)
    salary_string = re.sub('(?<=\d)\s(?=\d)', '', salary_string)  # уберем пробелымежду цифрами (внцри чисел)
    salary_string = salary_string.lower()
    words = re.findall(r'\w+', salary_string)  # составим список слов из строки

    salary_from, salary_to, salary_currency = None, None, None

    if words:
        if len(words) > 2:
            salary_currency = words[2]

        if words.count('от') != 0:
            salary_from = int(words[1])
        elif words.count('до') != 0:
            salary_to = int(words[1])
        elif words.count('по') != 0:
            pass
        else:
            salary_from = int(words[0])
            salary_to = words[1]

    return salary_from, salary_to, salary_currency, words

a, b, c, words = salary_parser('12 000 — 15 000 руб.')
print(words)
print(a, b, c)