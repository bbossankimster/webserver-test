import sys, os
import pytest
from fakers import random_string, random_list_of_strings
sys.path.append(os.getcwd())
from apps.webserver_test.utils.hostnames import hostname_to_ips

REAL_DOMAINS = ['yandex.ru', 'google.com', 'yahoo.com']
UNREAL_DOMAINS = random_list_of_strings(3, 5)


@pytest.mark.skipif("--dont_skip_real" not in sys.argv, reason='run with --dont_skip_real')
def test_to_ips_no_err():
    for domain in REAL_DOMAINS:
        ips = hostname_to_ips(domain)
        assert type(ips) == list
        assert len(ips) > 0


@pytest.mark.skipif("--dont_skip_real" not in sys.argv, reason='run with --dont_skip_real')
def test_to_ips_err():
    for domain in UNREAL_DOMAINS:
        with pytest.raises(ValueError, match=r".*EXCEPTION ERROR: can not resolve .*"):
            ips = hostname_to_ips(domain)
