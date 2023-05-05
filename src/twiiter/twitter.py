import aiohttp

from datetime import datetime
from .twitter_auth_browser import TwitterAuthBrowser
from .twitter_auth_requests import TwitterAuthRequests
from src.exceptions import TwitterRequestAuthError

twitter_date_format = '%a %b %d %H:%M:%S +0000 %Y'


class TwitterParser:
    def __init__(self, login: str, password: str, nickname: str):
        self.login = login
        self.password = password
        self.nickname = nickname
        self.bearer = "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"
        self.cookies = None
        self.csrf_token = None

    async def new_tweets_generator(self, query: str, timestamp: datetime):
        scroll = ''
        break_flag = False
        while True:
            try:
                tweets, new_scroll = await self._get_tweets_by_query(query, scroll)
            except TwitterRequestAuthError:
                await self._update_cookies()
                continue

            if new_scroll == scroll:
                break_flag = True
            scroll = new_scroll

            new_tweets = list()
            for tweet in tweets:
                tweet_created_at = datetime.strptime(tweet['created_at'], twitter_date_format)
                if tweet_created_at > timestamp:
                    new_tweets.append(tweet)
                else:
                    break_flag = True

            yield new_tweets

            if break_flag:
                print(f"Закончили поиск для {query}")
                break

    async def _get_tweets_by_query(self, query: str, scroll: str) -> dict:
        link = f"https://twitter.com/i/api/2/search/adaptive.json"

        params = [
            ('q', query),
            ('query_source', 'typed_query'),
            ('pc', '1'),
            ('tweet_mode', 'extended'),
            ('tweet_search_mode', 'live')
        ]

        if scroll:
            params.append(('cursor', scroll))

        headers = {
            "cookie": self.cookies,
            "authorization": self.bearer,
            "x-csrf-token": self.csrf_token
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(link, headers=headers, params=params) as response:
                status_code = response.status
                if status_code == 403:
                    # Надо поменять x-guest-token
                    raise TwitterRequestAuthError('Forbidden.')
                data = await response.json()

        # Получаем твиты
        tweets = data['globalObjects']['tweets']

        tweets = [tweet_info for tweed_id, tweet_info in tweets.items()]

        # Получаем scroll для следующего поиска
        instructions = data['timeline']['instructions']

        # При первом и последующих запросах scroll расположен в разных местах
        if not scroll:
            scroll = instructions[0]['addEntries']['entries'][-1]['content']['operation']['cursor']['value']
        else:
            scroll = instructions[2]['replaceEntry']['entry']['content']['operation']['cursor']['value']

        return tweets, scroll

    async def auth(self, auth_type: str):
        if auth_type == 'browser':
            cookies = await TwitterAuthBrowser.auth(self.login, self.password, self.nickname)
        elif auth_type == 'requests':
            cookies = await TwitterAuthRequests.auth(self.login, self.password, self.nickname)
        else:
            raise RuntimeError(f'Unknown auth_type - {auth_type}')

        cookies_str, csrf_token = self._prepare_cookies(cookies)
        self.cookies = cookies_str
        self.csrf_token = csrf_token
        print("Auth success!")

    @staticmethod
    def _prepare_cookies(cookies):
        needed_cookies = ['auth_token', 'ct0']

        cookies_str = ""
        csrf_token = ""
        for cookie in cookies:
            if cookie['name'] in needed_cookies:
                cookies_str += f"{cookie['name']}={cookie['value']}; "

            if cookie['name'] == 'ct0':
                csrf_token = cookie['value']

        for cookie_name in needed_cookies:
            if cookie_name not in cookies_str:
                raise RuntimeError(f'No needed cookies - {cookie_name}, {cookies}')

        if not csrf_token:
            raise RuntimeError(f'No csrf token {cookies}')

        return cookies_str, csrf_token

    async def _update_cookies(self):
        pass