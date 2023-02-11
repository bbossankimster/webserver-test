import sys,os
from email.mime.multipart import MIMEMultipart
import io
import pytest
from fakers import random_buffered_csv, random_string
import random


sys.path.append(os.getcwd())
from apps.webserver_test.utils.mail_attachment import add_attachment, attach_scv

@pytest.fixture(scope='function')
def msg():
    return MIMEMultipart()


@pytest.fixture(scope='session')
def buffered_csv():
    buffered_csv = random_buffered_csv()
    print(buffered_csv.getvalue())
    print(buffered_csv.getvalue().encode('ascii', 'surrogateescape'))
    return buffered_csv


@pytest.fixture(scope='function')
def make_fake_attchmnt():
    def _make_attchmnt(incorrect_keys=False, make_incorrect_csv=False):
        if incorrect_keys:
            return [{}, {"type": "text"},  {"type": "csv"}, {"type": "html"}]
        elif make_incorrect_csv:
            return [
                {"type": "text", "content": random_string()},
                {"type": "csv", "content": random_string()},
                {"type": "html", "content": io.StringIO(random_string())}
                ]
        else:
            return [
                {"type": "text", "content": random_string()},
                {"type": "html", "content": random_string()},
                {"type": "csv", "content": io.StringIO(random_string())}
                ]
    return _make_attchmnt


def test_attach_scv(msg, buffered_csv):
    content = buffered_csv.getvalue().encode('ascii', 'surrogateescape')
    assert msg._payload == []
    attach_scv(msg, buffered_csv, "sample.csv")
    assert msg._payload != [] and len(msg._payload) == 1
    assert msg._payload[0].get_payload(decode=True) == content


def test_add_attachment_incorrect_keys(msg, make_fake_attchmnt):
    fake_attchmnt = make_fake_attchmnt(incorrect_keys=True)
    for attchmnt in fake_attchmnt:
        print(attchmnt)
        assert set(attchmnt.keys()).intersection(set(["type", "content"])) != set(["type", "content"])
    assert len(msg._payload) == 0
    with pytest.raises(ValueError):
        add_attachment(msg, fake_attchmnt)


def test_add_attachment_incorrect_csv(msg, make_fake_attchmnt):
    fake_attchmnt = make_fake_attchmnt(incorrect_keys=False, make_incorrect_csv=True)
    for attchmnt in fake_attchmnt:
        assert set(attchmnt.keys()).intersection(set(["type", "content"])) == set(["type", "content"])
    assert len(msg._payload) == 0
    with pytest.raises(TypeError):
        add_attachment(msg, fake_attchmnt)


def test_add_attachment_correct_all(msg, make_fake_attchmnt):
    fake_attchmnt = make_fake_attchmnt(incorrect_keys=False, make_incorrect_csv=False)
    for attchmnt in fake_attchmnt:
        assert set(attchmnt.keys()).intersection(set(["type", "content"])) == set(["type", "content"])
    assert len(msg._payload) == 0
    add_attachment(msg, fake_attchmnt)
    assert len(msg._payload) == 3
    assert type(msg._payload) == list
