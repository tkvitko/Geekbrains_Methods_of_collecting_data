import re

str = 'з/п не указана'

def process_salary(salary_string):
    # функция для разбиения строки с зарплатой на подстроки (от, до, валюта)
    salary_string = re.sub('(?<=\d)\s(?=\d)', '', salary_string)  # уберем пробелымежду цифрами (внцри чисел)
    salary_string = salary_string.lower()
    words = re.findall(r'\w+', salary_string)  # составим список слов из строки
    print(words)

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

a, b, c = process_salary(str)
print(a, b, c)