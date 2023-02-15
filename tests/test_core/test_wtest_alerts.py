import sys,os
import pytest
from io import StringIO
import pandas
sys.path.append(os.getcwd())
from apps.webserver_test.core.webserver_test import (WebSrvTestWithAlerts, send_req, ds, WebSrvTestWithAlerts, WTestMailSender)
from apps.webserver_test.core.logs.collector import LogsCollectorAfterTest, LOG_COL


@pytest.fixture()
def wtest_do_run(mocker, resolved_hosts, host_groups, services, sttngs, read_logs, mixed_http_response):
    """Returns wtest objects, 2 cases: with and without logs"""
    is_logs_empty, read_logs_func = read_logs
    mocker.patch.object(ds, "hostname_to_ips", return_value=resolved_hosts)
    mocker.patch.object(send_req, "send_request_async", new=mixed_http_response)
    mocker.patch.object(LogsCollectorAfterTest, "_read_logs_by_ssh", new=read_logs_func)
    wtest = WebSrvTestWithAlerts(host_groups, services, rqst_stngs=sttngs, key="fake_key")
    wtest.run()
    return wtest, is_logs_empty


def test_init_attrs(wtest_with_logs_init):
    wtest = wtest_with_logs_init
    attrs = sorted(wtest.__dict__.keys())
    assert attrs == [
        'dataset', 'err_threshold', 'findings', 'host_groups', 'hosts_df', 'key', 'logs', 'rqst_stngs',
        'rqsts_df', 'services', 'txt_summary']
    # counts
    assert len(attrs) == 11
    # values
    non_empty_attrs = [attr for attr in attrs if getattr(wtest, attr) is not None]
    assert non_empty_attrs == ['err_threshold', 'host_groups', 'key', 'rqst_stngs', 'services', 'txt_summary']
    global attrs_init
    attrs_init = set(attrs)


def test_run_attrs(wtest_do_run):
    wtest, is_logs_empty = wtest_do_run
    attrs = sorted(wtest.__dict__.keys())
    assert len(attrs) == 14
    assert attrs == [
        'anlzr', 'dataset', 'err_threshold', 'errors', 'findings','host_groups', 'hosts_df', 'key',
        'logs', 'no_errors', 'rqst_stngs', 'rqsts_df', 'services', 'txt_summary']
    global attrs_run
    attrs_run = set(attrs)


def test_run_result_txt(wtest_do_run):
    wtest, is_logs_empty = wtest_do_run
    # 1) res txt
    res_txt = wtest.txt_summary["no_errors"]
    assert res_txt.split("\n")[0] == "customer_102.site.com, server 1 (192.168.101.8): reports, status_code 200"
    assert sorted([*wtest.txt_summary]) == ['all', 'errors', 'no_errors']
    # 2) total requests with errors and without errors
    assert len(wtest.txt_summary["no_errors"].split("\n")) == len(wtest.no_errors.index)
    assert len( wtest.txt_summary["errors"].split("\n")) == len(wtest.errors.index)


def test_run_result_df(wtest_do_run):
    wtest, is_logs_empty = wtest_do_run
    dataset_col = list(wtest.dataset.columns)
    rqsts_col = list(wtest.rqsts_df.columns)
    assert len(dataset_col) == 7
    assert len(rqsts_col) == 12
    assert dataset_col == [
        'group_type', 'group_name', 'id_in_group', 'host_label', 'host_ip', 'url', 'service_name']
    assert set(rqsts_col).difference(set(dataset_col)) == {
        'status_code', 'resp_out', 'row_id', 'exception_request', 'tries'}


def test_run_result_logs(wtest_do_run):
    wtest, is_logs_empty = wtest_do_run
    assert wtest.err_threshold == 10
    if is_logs_empty:
        assert wtest.logs is None
    else:
        assert wtest.logs is not None
        logs_attrs = sorted(wtest.logs.__dict__.keys())
        assert logs_attrs == ['columns_to_print', 'raw']
        assert len(wtest.logs.raw) == 2
        for id, log in wtest.logs.raw:
            assert isinstance(log, pandas.core.frame.DataFrame)
            assert not log.empty
            print(log)


def test_attrs_diff_after_run():
    assert attrs_run.difference(attrs_init) == {'errors', 'no_errors', 'anlzr'}


def sendmail(self):
    message = self._make_msg()
    return None

class TestSendmail:
    def test_do_no_args(self, wtest_do_run):
        wtest, is_logs_empty = wtest_do_run
        with pytest.raises(TypeError, match=r".*required positional arguments.*"):
            wtest.sendmail()

    def test_do_fake(self, wtest_do_run, conf, mocker):
        wtest, is_logs_empty = wtest_do_run
        mocker.patch.object(WTestMailSender, "sendmail", new=sendmail)
        spy = mocker.spy(WTestMailSender, "_make_msg")
        is_failed = wtest.sendmail(conf.auth, conf.send_to_errors, "#wtest (from pytest)")
        assert spy.call_count == 1
        msg = spy.spy_return
        assert msg is not None
        assert len(msg._payload) == 2
        html = msg._payload[0].get_payload(decode=True).decode()
        assert is_failed is None
        if is_logs_empty:
            assert "Логи веб серверов" not in html
            assert wtest.logs is None
        else:
            assert "Логи веб серверов" in html
            assert wtest.logs is not None

    @pytest.mark.skipif("--dont_skip_real" not in sys.argv, reason='run with --dont_skip_real')
    def test_do_real(self, wtest_do_run, conf):
        wtest, is_logs_empty = wtest_do_run
        is_failed = wtest.sendmail(conf.auth, conf.send_to_errors, "#wtest (from pytest)")
        assert is_failed is None
