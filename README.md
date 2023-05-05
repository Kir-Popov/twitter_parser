# twitter_parser

Сервис позволяет асинхронно собирать посты из твиттера, используя advanced search. 
Написан модуль авторизации через эмулятор браузера (pyppeteer) и простые запросы.


## Установка

Должен быть установлен python 3.9 +

git clone https://github.com/Kir-Popov/twitter_parser.git

cd twitter_parser

pipenv install

pipenv shell

### в папке config надо добавить файл config.py, в который указать креды от твитера!



## Использование

Разберем main.py

```python 
from src import TwitterParser
from config.config import login, password, nickname

async def main():
    # TwitterParser - класс, который реализвует всю логику
    twitter_parser = TwitterParser(login, password, nickname)
    
    # Перед началом работы нужна авторизация в твиттере.
    # auth_type может быть либо requests либо browser
    # советую потестить browser, интересно выглядит)
    await twitter_parser.auth(auth_type='requests')

    # для примеры запросы состоят из одного ключевого слова
    queries = ['BMSTU', 'MSTU', 'MIPT']

    # Временная отметка, в данном случае 3 марта
    # Обязательна для работы генератора new_tweets_generator
    timestamp = datetime(2023, 3, 1)
    
    
    # так как получение постов реализовано через асинхронные генераторы, то
    # можно создать много таких генераторов, и объединить их.
    generators = []
    for query in queries:
        gen = twitter_parser.new_tweets_generator(query, timestamp)
        generators.append(gen)

    # мердж генераторов, мощная штука
    combine = stream.merge(*generators)
    async with combine.stream() as streamer:
        async for reports in streamer:
            print(f"new reports - {reports}")
```

для запуска необходимо использовать команду:
### python3 main.py
