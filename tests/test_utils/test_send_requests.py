import sys,os
import aiohttp
import asyncio
import random
import pytest

sys.path.append(os.getcwd())
from apps.webserver_test.utils.send_requests import send_request_async

URLS = ["http://ip-api.com", "https://customer_1.site.com/", "https://2ip.ru/"]

# http://wrong-name.com

@pytest.fixture(scope='session')
def fake_urls():
    counts = random.sample(range(4, 10), 3)
    print(counts)
    return random.sample(URLS, counts=counts, k=10)


@pytest.fixture(scope='session')
def fake_sttngs():
    return {
        "timeout": random.randint(1, 5),
        "max_retries": random.randint(0, 2)
    }



@pytest.mark.asyncio
async def test_send_request_async(fake_urls, fake_sttngs):
    assert type(fake_sttngs) == dict and fake_sttngs != {}
    assert type(fake_urls) == list and len(fake_urls) == 10

    async with aiohttp.ClientSession() as session:
        tasks = [asyncio.create_task(send_request_async(session, url, fake_sttngs)) for url in fake_urls]
        results = await asyncio.gather(*tasks, return_exceptions=False)
        assert len(results) == 10
        cntr = -1
        for result in results:
            cntr += 1
            assert len(result) == 4
            status_code, resp_out, exception_request, tries = result
            # 1) status_code
            assert type(status_code) == str
            if type(status_code) == str:
                assert len(status_code) >= 3
            # 2) resp_out
            assert type(resp_out) is bytes or type(resp_out) is str
            # 3) exception_request
            if type(exception_request) == str:
                print(status_code)
                print(exception_request)
                print(fake_urls[cntr])
            assert type(exception_request) is type(None) or type(exception_request) is str
            # 4) tries
            assert type(tries) == int
