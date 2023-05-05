import asyncio

from src import TwitterParser
from aiostream import stream
from config.config import login, password, nickname
from datetime import datetime


async def main():
    twitter_parser = TwitterParser(login, password, nickname)
    await twitter_parser.auth(auth_type='requests')

    # для примеры запросы состоят из одного ключевого слова
    queries = ['BMSTU', 'MSTU', 'MIPT']

    # Временная отметка, в данном случае 3 марта
    timestamp = datetime(2023, 3, 1)

    generators = []
    for query in queries:
        gen = twitter_parser.new_tweets_generator(query, timestamp)
        generators.append(gen)

    # мердж генераторов, мощная штука
    combine = stream.merge(*generators)
    async with combine.stream() as streamer:
        async for reports in streamer:
            print(f"new tweets - {reports}")

if __name__ == '__main__':
    asyncio.run(main())
