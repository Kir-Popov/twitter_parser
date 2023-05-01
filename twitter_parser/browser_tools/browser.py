import pyppeteer
from contextlib import asynccontextmanager
import aiohttp

from pyppeteer.browser import Browser as PyppeteerBrowser

TIMEOUT = 30000

BROWSER_SIZE = (1280, 1024)

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36"


class Browser:
    browser: PyppeteerBrowser
    params: dict

    def __init__(self, headless=False, proxy=None, args=None):

        if not args:
            args = list()

        if proxy:
            args.append(f"--proxy-server={proxy}")

        self.params = {
            'args': args,
            'headless': headless,
            'autoClose': True
        }

        self.browser = None

    async def __aenter__(self):
        self.browser = await pyppeteer.launch(**self.params)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.browser.close()
        self.browser = None

    @asynccontextmanager
    async def open_page(self, url: str, timeout: int = TIMEOUT, user_agent: str = USER_AGENT,
                        browser_size: tuple = BROWSER_SIZE, extra_headers: dict = None
                        ):

        if not self.browser:
            raise RuntimeError('browser not stated, use __aenter__ to create it.')

        page = await self.browser.newPage()

        if extra_headers:
            await page.setExtraHTTPHeaders(extra_headers)

        browser_size = {
            "width": browser_size[0],
            "height": browser_size[1]
        }

        await page.emulate(viewport=browser_size, userAgent=user_agent)
        await page.goto(url=url, timeout=timeout, waitUntil='domcontentloaded')

        try:
            yield page
        finally:
            await page.close()
