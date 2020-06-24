# 2. Изучить список открытых API (https://www.programmableweb.com/category/all/apis).
# Найти среди них любое, требующее авторизацию (любого типа).
# Выполнить запросы к нему, пройдя авторизацию. Ответ сервера записать в файл.

import requests
from pprint import pprint

# Enter your access token here:
access_token = '<your_toke_here>'

vk_endpoit = 'https://api.vk.com/method/'
api_method = 'groups.get'
params = {'v': 5.52,
          'access_token': access_token}

response = requests.get(f'{vk_endpoit}{api_method}', params=params)
data = response.json()
pprint(data)

with open('groups.json', 'wb') as f:
    f.write(response.content)
