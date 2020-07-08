# 2) Написать программу, которая собирает «Хиты продаж» с сайта техники mvideo и складывает данные в БД.
# Магазины можно выбрать свои. Главный критерий выбора: динамически загружаемые товары

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from pymongo import MongoClient
from pymongo import errors
from selenium.webdriver.chrome.options import Options
import time


def save_data_to_db(data):
    # функция записи в БД. Возвращает 1, если элемент был добавлен
    try:
        db.goods.replace_one(data, data, upsert=True)  # добавится только товар, которого нет в БД
    except errors.DuplicateKeyError:
        pass
        return 0
    else:
        return 1


# Параметры работы с БД
client = MongoClient('localhost', 27017)
db = client['mvideo_db']

# Параметры работы с mail.ru
chrome_options = Options()
chrome_options.add_argument('start-maximized')
driver = webdriver.Chrome('./chromedriver', options=chrome_options)
base_url = 'https://www.mvideo.ru/'
driver.get(base_url)

items_list = []
items_count = 0
while True:

    names = driver.find_elements_by_xpath("//*[contains(text(),'Хиты продаж')]/ancestor::div[@class='section']//li//h4")
    prices = driver.find_elements_by_xpath(
        "//*[contains(text(),'Хиты продаж')]/ancestor::div[@class='section']//li//div[@class='c-pdp-price__current']")

    # Подгрузка элементов на сайте сделана так:
    # - при нажатии на кнопку "next page" новые 4 li появляются в начале списка
    # - элементы с предыдущих страниц перемещаются в конец списка и теряют цену (!)
    # - в итоге перед каждым нажатием кнопки нужно брать на анализ 4 элемента из начала списка

    for i in range(4):
        item = {}
        item['name'] = names[i].get_attribute('title')
        item['price'] = prices[i].text.replace(u'¤', u'')
        items_list.append(item)
        items_count += save_data_to_db(item)

    try:
        button_xpass = "//*[contains(text(),'Хиты продаж')]/ancestor::div[@class='section']//a[@class='next-btn sel-hits-button-next']"
        button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, button_xpass))
        )
        button.click()
        time.sleep(2)
    except:
        break

print(f'Проанализировано товаров: {items_count}')
