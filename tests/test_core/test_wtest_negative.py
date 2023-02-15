import sys,os
import random
import pytest


sys.path.append(os.getcwd())
from apps.webserver_test.core.webserver_test import (
    CommonWebSrvTest, send_req, ds)

HTTP_CODES = ["TimeoutError", '200', '502', '503', '407', '490', '404']

FAKE_HOST_GROUPS = ["customer_102.site.com"]
FAKE_SERVICES = 'reports,support,analytics,store'.split(",")
FAKE_SETTINGS = {
    "timeout": random.randint(1, 5),
    "max_retries": random.randint(0, 2)
    }

@pytest.fixture
def get_wtest_obj(mocker):
    def _get_wtest_obj(return_mocked=False):
        mocked_send_request = mocker.patch.object(send_req, "send_request_async", return_value=["503", "", None, 1])
        mocked_hostname_to_ips = mocker.patch.object(ds, "hostname_to_ips", return_value=['192.168.101.8', '192.168.101.9'])
        wtest = CommonWebSrvTest(FAKE_HOST_GROUPS, FAKE_SERVICES, FAKE_SETTINGS)
        wtest.run()
        if return_mocked:
            return mocked_send_request, mocked_hostname_to_ips
        else:
            return wtest
    return _get_wtest_obj


def test_dataset(get_wtest_obj):
    wtest = get_wtest_obj(return_mocked=False)
    # 1) hosts
    assert type(wtest.host_groups) == list and len(wtest.host_groups) == 1
    assert list(wtest.hosts_df['host_ip'].unique()) == ['192.168.101.8', '192.168.101.9']
    # 2) services
    assert wtest.services == {'customer_102.site.com': ['reports', 'support', 'analytics', 'store']}


def test_mocked_exec(get_wtest_obj):
    mocked_send_request, mocked_hostname_to_ips = get_wtest_obj(return_mocked=True)
    assert mocked_send_request.call_count == 2 * 4
    assert mocked_hostname_to_ips.call_count == 1


def test_result(get_wtest_obj):
    wtest = get_wtest_obj(return_mocked=False)
    # 1) txt
    assert sorted([*wtest.txt_summary]) == ['all', 'errors']
    res_txt = wtest.txt_summary["errors"]
    assert res_txt.split("\n")[0] == "customer_102.site.com, server 1 (192.168.101.8): reports, status_code 503"
    # 2) dataframes
    assert wtest.errors.empty == False
    assert wtest.no_errors.empty == True
    assert list(wtest.rqsts_df.columns) == [
        'group_type', 'group_name', 'id_in_group', 'host_label', 'host_ip', 'url', 'service_name',
        'status_code', 'resp_out', 'exception_request', 'tries', 'row_id']


def test_analyze(get_wtest_obj):
    wtest = get_wtest_obj(return_mocked=False)
    after_analyze = wtest.analyze()
    assert after_analyze == 'Критическая ошибка!\n\
2 сервер(а) отключен(ы) и/или все приложения не работают\n\
192.168.101.8\n\
192.168.101.9\n------'