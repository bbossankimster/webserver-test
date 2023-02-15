import pytest
import random
import sys,os
from io import StringIO
import pandas
import re
sys.path.append(os.getcwd())
from apps.webserver_test import (WebSrvTestWithLogs, WtestSettings)
from apps.webserver_test.core.logs.collector import LOG_COL

FAKE_LOGS = '''
192.168.50.1 HTTP/1.1 "14/Feb/2023:21:29:31 +0000" "GET /reports.html HTTP/1.1" 404 308 "Python/3.10 aiohttp/3.8.3" {ip}
192.168.50.1 HTTP/1.1 "14/Feb/2023:21:29:31 +0000" "GET /support.html HTTP/1.1" 200 267 "Python/3.10 aiohttp/3.8.3" {ip}
192.168.50.1 HTTP/1.1 "14/Feb/2023:21:29:31 +0000" "GET /store.html HTTP/1.1" 200 265 "Python/3.10 aiohttp/3.8.3" {ip}
192.168.50.1 HTTP/1.1 "14/Feb/2023:21:29:31 +0000" "GET /analytics.html HTTP/1.1" 200 269 "Python/3.10 aiohttp/3.8.3" {ip}
'''


@pytest.fixture(scope='module')
def host_groups():
    return ["customer_102.site.com"]


@pytest.fixture(scope='module')
def resolved_hosts():
    return ['192.168.101.8', '192.168.101.9', '192.168.101.10']


@pytest.fixture(scope='module')
def services():
    return 'reports,support,analytics,store'.split(",")


@pytest.fixture(scope='module')
def raw_logs():
    return FAKE_LOGS


@pytest.fixture(scope='module')
def sttngs():
    return {"timeout": random.randint(1, 5), "max_retries": random.randint(0, 2)}


@pytest.fixture(scope='module')
def wtest_with_logs_init(host_groups, services, sttngs):
    wtest = WebSrvTestWithLogs(host_groups, services, rqst_stngs=sttngs, key="fake_key")
    return wtest


is_logs_empty = [False, True]
@pytest.fixture(params=is_logs_empty, ids=["empty_logs_{}".format(v) for v in is_logs_empty])
def read_logs(request, raw_logs):
    async def non_empty_logs(self, cmd):
        ips = re.findall(r'\d+.\d+.\d+.\d+', cmd)
        return pandas.read_csv(StringIO(raw_logs.format(ip=ips[0])), delimiter=' ', skipinitialspace=True, names=LOG_COL)

    async def empty_logs(self, cmd):
        return pandas.DataFrame(columns=LOG_COL)
    is_logs_empty = request.param
    if is_logs_empty:
        return (True, empty_logs)
    return (False, non_empty_logs)


@pytest.fixture(scope='module')
def mixed_http_response():
    async def _mixed_http_response(session, url, stngs):
        if "192.168.101.8" in url:
            return ["200", "STUB_OUT", None, 1]
        else:
            return ["503", "", None, 1]
    return _mixed_http_response

@pytest.fixture(scope='module')
def conf():
    print(os.path.join(os.path.dirname(__file__), "wtest.conf"))
    conf = WtestSettings(os.path.join(os.path.dirname(__file__), "wtest.conf"))
    assert conf.auth["username"] != ""
    return conf
