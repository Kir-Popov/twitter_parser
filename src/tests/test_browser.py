import asyncio

from src.browser_tools.browser import Browser


async def test_example():
    async with Browser() as browser:
        async with browser.open_page(url="https://example.com/") as page:
            html = await page.content()
            if "Example Domain" in html:
                return True

    return False


async def tests():
    assert await test_example(), True

if __name__ == '__main__':
    asyncio.run(tests())
