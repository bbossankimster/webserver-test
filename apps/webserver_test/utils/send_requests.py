import aiohttp
import asyncio

ERRORS_FAMILY = ['503', '502']


async def send_request_async(session, url, stngs):
    timeout = stngs['timeout']
    max_retries = stngs['max_retries']
    tries = 0
    is_ok = False
    while tries <= max_retries and is_ok is False:
        exception_request = None
        status_code = "INCOMPLETE"
        resp_out = "INCOMPLETE"
        try:
            resp = await session.get(url, timeout=timeout)
            status_code = str(resp.status)
            if status_code in ERRORS_FAMILY:
                is_ok = False
            else:
                is_ok = True
            resp_out = await resp.read()
            resp.close()
        except Exception as e:
            is_ok = False
            exception_request = str(type(e))
            if exception_request == "<class 'asyncio.exceptions.TimeoutError'>":
                status_code = "TimeoutError"
        finally:
            tries += 1
    return [status_code, resp_out, exception_request, tries]


async def websrvtest_tasks(dataset, request_stngs):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for index in dataset.index:
            task = asyncio.create_task(send_request_async(session, dataset.loc[index]['url'], request_stngs))
            tasks.append(task)
        result = await asyncio.gather(*tasks, return_exceptions=False)
    return result
