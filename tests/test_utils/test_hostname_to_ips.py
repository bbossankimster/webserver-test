import sys, os
import socket
import pytest
from fakers import random_string, random_list_of_strings
sys.path.append(os.getcwd())
from apps.webserver_test.utils.hostnames import hostname_to_ips

REAL_DOMAINS = ['yandex.ru', 'google.com', 'yahoo.com']
UNREAL_DOMAINS = random_list_of_strings(3, 5)


def test_gethostsbyname():
    with pytest.raises(socket.gaierror):
        hosts_data = socket.gethostbyname_ex(random_string())


def test_to_ips_no_err():
    for domain in REAL_DOMAINS:
        ips = hostname_to_ips(domain)
        assert type(ips) == list
        assert len(ips) > 0


def test_to_ips_err():
    for domain in UNREAL_DOMAINS:
        with pytest.raises(ValueError, match=r".*EXCEPTION ERROR: can not resolve .*"):
            ips = hostname_to_ips(domain)
