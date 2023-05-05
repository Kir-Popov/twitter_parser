import asyncio
from config.config import login, password, nickname


from src.twiiter.twitter_auth_requests import TwitterAuthRequests


async def test():
    await TwitterAuthRequests.auth(login, password, nickname)


if __name__ == '__main__':
    asyncio.run(test())
