# 1. Посмотреть документацию к API GitHub, разобраться как вывести список репозиториев для конкретного пользователя,
# сохранить JSON-вывод в файле *.json.

import requests
from pprint import pprint

# Enter your access token here:
token = '<your_toke_here>'

github_endpoit = 'https://api.github.com/graphql'
headers = {'Authorization': f'bearer {token}'}
data = '{"query": "query { viewer { repositories(last: 10) {nodes {name}} }}"}'

response = requests.post(github_endpoit, headers=headers, data=data)
data = response.json()
pprint(data["data"]["viewer"]["repositories"]["nodes"])

with open('repos.json', 'wb') as f:
    f.write(response.content)
    