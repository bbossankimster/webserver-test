import sys,os
sys.path.append(os.getcwd())
import pytest
import apps.webserver_test.utils.dataset as dataset
import pandas
import random

HOSTS_COL = ["group_type", "group_name", "id", "id_in_group", "host_label", "host_ip"]
IPS = [f'192.168.100.{num}' for num in random.sample(range(1, 255), 10)]
DOMAIN = "random.domain.com"

@pytest.fixture(scope='session')
def tested_hosts_df():
    cntr = 0
    df_list = []
    for ip in IPS:
        cntr += 1
        df_list.append(pandas.DataFrame([["domain", DOMAIN, cntr, cntr, f"server {cntr}", ip]], columns=HOSTS_COL))
    return pandas.concat(df_list).set_index(["id"], drop=True)


def test_tested_data(tested_hosts_df):
    assert type(tested_hosts_df) == pandas.core.frame.DataFrame
    assert list(tested_hosts_df.index)[0] == 1
    assert len(tested_hosts_df.index) == 10
    assert len(tested_hosts_df.columns) == 5


def test_make_dateset(tested_hosts_df):
    serv_list = ['reports', 'analytics']
    ds = dataset.make_dataset(tested_hosts_df, {DOMAIN: serv_list})
    assert type(ds) == pandas.core.frame.DataFrame
    assert list(ds.index)[0] == 0
    assert len(ds.index) == 20
    assert len(ds.index) == len(serv_list) * len(tested_hosts_df.index)
    assert len(ds.columns) == 7
    assert set(ds.columns).difference(set(tested_hosts_df.columns)) == set(['url', 'service_name'])
