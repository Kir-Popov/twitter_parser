import asyncio
import re

import aiohttp

from src.exceptions import AuthError

bearer_token = "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs=1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"


class TwitterAuthRequests:
    @classmethod
    async def auth(cls, login, password, nickname):
        x_guest_token = await cls._get_x_guest_token()
        headers = {
            "x-guest-token": x_guest_token,
            "authorization": bearer_token,
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
            "x-twitter-active-user": "yes"
        }

        params = [
            ("flow_name", "login")
        ]
        url = "https://api.twitter.com/1.1/onboarding/task.json"
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.post(url, params=params) as response:
                data = await response.json()
                flow_token = data['flow_token']

            body = {
                "flow_token": flow_token,
            }
            async with session.post(url, json=body) as response:
                data = await response.json()
                flow_token = data['flow_token']

            body = {
                "flow_token": flow_token,
                "subtask_inputs": [
                    {
                        "subtask_id": "LoginEnterUserIdentifierSSO",
                        "settings_list": {
                            "setting_responses": [
                                {
                                    "key": "user_identifier",
                                    "response_data": {
                                        "text_data": {
                                            "result": login
                                        }
                                    }
                                }
                            ],
                            "link": "next_link"
                        }
                    }
                ]
            }

            async with session.post(url, json=body) as response:
                data = await response.json()
                flow_token = data['flow_token']
                subtask = data['subtasks'][0]['subtask_id']
                if subtask == "LoginEnterAlternateIdentifierSubtask":
                    body = {
                        "flow_token": flow_token,
                        "subtask_inputs": [
                            {
                                "subtask_id": "LoginEnterAlternateIdentifierSubtask",
                                "enter_text": {
                                    "text": nickname,
                                    "link": "next_link"
                                }
                            }
                        ]
                    }

                    async with session.post(url, json=body) as sub_response:
                        data = await sub_response.json()
                        flow_token = data['flow_token']

            body = {
                "flow_token": flow_token,
                "subtask_inputs": [
                    {
                        "subtask_id": "LoginEnterPassword",
                        "enter_password": {
                            "password": password,
                            "link": "next_link"
                        }
                    }
                ]
            }

            async with session.post(url, json=body) as response:
                data = await response.json()
                flow_token = data['flow_token']

            body = {
                "flow_token": flow_token,
                "subtask_inputs": [
                    {
                        "subtask_id": "AccountDuplicationCheck",
                        "check_logged_in_account": {
                            "link": "AccountDuplicationCheck_false"
                        }
                    }
                ]
            }

            async with session.post(url, json=body) as response:
                data = await response.json()
                if response.status != 200:
                    raise AuthError(f'{data}')

                cookies = session.cookie_jar.filter_cookies("https://twitter.com/")

                cookies_list = list()
                for cookie_name, value in cookies.items():
                    cookies_list.append(
                        {
                            "name": cookie_name,
                            "value": value.value
                        }
                    )

            return cookies_list

    @classmethod
    async def _get_x_guest_token(cls):
        headers = {
            'authorization': bearer_token
        }
        async with aiohttp.ClientSession() as session:
            async with session.post("https://api.twitter.com/1.1/guest/activate.json", headers=headers) as response:
                data = await response.json()
                return data['guest_token']
