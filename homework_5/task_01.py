# 1) Написать программу, которая собирает входящие письма из своего или тестового почтового ящика
# и сложить данные о письмах в базу данных (от кого, дата отправки, тема письма, текст письма полный)
# Логин тестового ящика: study.ai_172@mail.ru
# Пароль тестового ящика: NextPassword172

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from pymongo import MongoClient
from pymongo import errors
import time


def save_data_to_db(data):
    # функция записи в БД. Возвращает 1, если письмо было добавлено
    try:
        db.mails_new.replace_one(data, data, upsert=True)  # добавится только письмо, которого нет в БД
    except errors.DuplicateKeyError:
        pass
        return 0
    else:
        return 1


# Параметры работы с БД
client = MongoClient('localhost', 27017)
db = client['mails_db']

# Параметры работы с mail.ru
username = 'study.ai_172@mail.ru'
password = 'NextPassword172'
driver = webdriver.Chrome('./chromedriver')
driver.get('https://e.mail.ru/')

# Ввод логина
elem = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.NAME, 'username'))
)
elem.send_keys(username)
elem.send_keys(Keys.ENTER)

# Ввод пароля
time.sleep(1)
elem = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.NAME, 'password'))
)
elem.send_keys(password)
elem.send_keys(Keys.ENTER)

# Составление списка url писем
time.sleep(4)
letters_urls_list = []

last = None
while True:
    letters = driver.find_elements_by_class_name('js-letter-list-item')
    # вынимаем url на письмо и кладем его в список, если его там еще нет
    for letter in letters:
        letter_url = letter.get_attribute('href')
        if letters_urls_list.count(letter_url) == 0:
            letters_urls_list.append(letter_url)
    # если есть, куда скроллить, скроллим
    if letters[-1] != last:
        last = letters[-1]
        actions = ActionChains(driver)
        actions.move_to_element(letters[-1])
        actions.perform()
        time.sleep(0.5)
    else:
        break

# Сбор информации из писем
letters_count = 0
for url in letters_urls_list[:4]:  # для проверки выставлено ограничение в несколько писем
    driver.get(url)
    letter_data = {}
    # Отправитель
    elem = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'letter-contact'))
    )
    letter_data['sender'] = elem.get_attribute('title')
    # Дата отправки
    elem = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'letter__date'))
    )
    letter_data['date'] = elem.text
    # Тема
    elem = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'thread__subject'))
    )
    letter_data['subject'] = elem.text
    # Текст
    elem = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'letter__body'))
    )
    letter_data['body'] = elem.text
    letters_count += save_data_to_db(letter_data)

print(f'Проанализировано писем: {letters_count}')
