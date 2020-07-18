# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from instaparser.items import InstaparserItem
import re
import json
from urllib.parse import urlencode
from copy import deepcopy


class InstagramSpider(scrapy.Spider):
    # атрибуты класса
    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['https://instagram.com/']
    insta_login = 'test_tkvitko'
    insta_pwd = '#PWD_INSTAGRAM_BROWSER:10:1595094631:AdVQAIs68c+qY19sux22mCJ0YIxAgWKqqe9bIoUdK1VYg4Jv5U0+V8hOBvNUd6g+D7FFfPpKneFrll3UBTvjXC53PdtJiQ6uVg91dsLh18u71LiZ/jpm0LlCmLcRzVuMtR0fFoDyWfreaQsdMr4llAHOaE+wNnXXnw=='  # TestGeekBrainsPassword
    inst_login_link = 'https://www.instagram.com/accounts/login/ajax/'
    parse_user = ['ai_machine_learning', 'great.foood']  # Пользователь, у которого собираем посты. Можно указать список

    graphql_url = 'https://www.instagram.com/graphql/query/?'
    posts_hash = '15bf78a4ad24e33cbd838fdb31353ac1'  # hash для получения данных по постах с главной страницы
    subscriptions_hash = 'd04b0a864b4b54837c0d870b0e77e076'  # hash для получения списка подписок

    def parse(self, response: HtmlResponse):  # Первый запрос на стартовую страницу
        csrf_token = self.fetch_csrf_token(response.text)  # csrf token забираем из html
        yield scrapy.FormRequest(  # заполняем форму для авторизации
            self.inst_login_link,
            method='POST',
            callback=self.user_parse,
            formdata={'username': self.insta_login, 'enc_password': self.insta_pwd},
            headers={'X-CSRFToken': csrf_token}
        )

    def user_parse(self, response: HtmlResponse):
        j_body = json.loads(response.text)
        if j_body['authenticated']:  # Проверяем ответ после авторизации
            for user in self.parse_user:
                yield response.follow(
                # Переходим на желаемую страницу пользователя. Сделать цикл для кол-ва пользователей больше 2-ух
                f'/{user}',
                callback=self.user_subscriptions_parse,
                cb_kwargs={'username': user}
            )

    # Функция парсинга подписок пользователя
    def user_subscriptions_parse(self, response: HtmlResponse, username):
        user_id = self.fetch_user_id(response.text, username)  # Получаем id пользователя
        variables = {'id': user_id,  # Формируем словарь для передачи даных в запрос
                     'first': 50,  # 12 постов. Можно больше (макс. 50)
                     'include_reel': True,
                     'fetch_mutual': False
                     }
        url_subscriptions = f'{self.graphql_url}query_hash={self.subscriptions_hash}&{urlencode(variables)}'  # Формируем ссылку для получения данных о постах
        yield response.follow(
            url_subscriptions,
            callback=self.user_subscriptions_continue,
            cb_kwargs={'username': username,
                       'user_id': user_id,
                       'variables': deepcopy(variables)}  # variables ч/з deepcopy во избежание гонок
        )

    def user_subscriptions_continue(self, response: HtmlResponse, username, user_id,
                                    variables):  # Принимаем ответ. Не забываем про параметры от cb_kwargs
        j_data = json.loads(response.text)
        page_info = j_data.get('data').get('user').get('edge_follow').get('page_info')
        if page_info.get('has_next_page'):  # Если есть следующая страница
            variables['after'] = page_info['end_cursor']  # Новый параметр для перехода на след. страницу
            url_subscriptions = f'{self.graphql_url}query_hash={self.subscriptions_hash}&{urlencode(variables)}'
            yield response.follow(
                url_subscriptions,
                callback=self.user_subscriptions_continue,
                cb_kwargs={'username': username,
                           'user_id': user_id,
                           'variables': deepcopy(variables)}
            )
        subscriptions = j_data.get('data').get('user').get('edge_follow').get('edges')  # Подписки
        for subscription in subscriptions:  # Перебираем посты, собираем данные
            item = InstaparserItem(
                user_id = user_id,
                subscription_id=subscription['node']['id'],
                subscription_name=subscription['node']['username'],
                subscription_photo=subscription['node']['profile_pic_url'],
                subscription=subscription['node']
            )
        yield item  # В пайплайн

    # def user_data_parse(self, response: HtmlResponse, username):
    #     user_id = self.fetch_user_id(response.text, username)  # Получаем id пользователя
    #     variables = {'id': user_id,  # Формируем словарь для передачи даных в запрос
    #                  'first': 12}  # 12 постов. Можно больше (макс. 50)
    #     url_posts = f'{self.graphql_url}query_hash={self.posts_hash}&{urlencode(variables)}'  # Формируем ссылку для получения данных о постах
    #     yield response.follow(
    #         url_posts,
    #         callback=self.user_posts_parse,
    #         cb_kwargs={'username': username,
    #                    'user_id': user_id,
    #                    'variables': deepcopy(variables)}  # variables ч/з deepcopy во избежание гонок
    #     )
    #
    # def user_posts_parse(self, response: HtmlResponse, username, user_id,
    #                      variables):  # Принимаем ответ. Не забываем про параметры от cb_kwargs
    #     j_data = json.loads(response.text)
    #     page_info = j_data.get('data').get('user').get('edge_owner_to_timeline_media').get('page_info')
    #     if page_info.get('has_next_page'):  # Если есть следующая страница
    #         variables['after'] = page_info['end_cursor']  # Новый параметр для перехода на след. страницу
    #         url_posts = f'{self.graphql_url}query_hash={self.posts_hash}&{urlencode(variables)}'
    #         yield response.follow(
    #             url_posts,
    #             callback=self.user_posts_parse,
    #             cb_kwargs={'username': username,
    #                        'user_id': user_id,
    #                        'variables': deepcopy(variables)}
    #         )
    #     posts = j_data.get('data').get('user').get('edge_owner_to_timeline_media').get('edges')  # Сами посты
    #     for post in posts:  # Перебираем посты, собираем данные
    #         item = InstaparserItem(
    #             user_id=user_id,
    #             photo=post['node']['display_url'],
    #             likes=post['node']['edge_media_preview_like']['count'],
    #             post=post['node']
    #         )
    #     yield item  # В пайплайн

    # Получаем токен для авторизации
    def fetch_csrf_token(self, text):
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    # Получаем id желаемого пользователя
    def fetch_user_id(self, text, username):
        matched = re.search(
            '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
        ).group()
        return json.loads(matched).get('id')
