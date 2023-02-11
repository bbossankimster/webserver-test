import sys,os
sys.path.append(os.getcwd())
import pickle
import string
import random
import apps.webserver_test.utils.dat_files as dat_files


def read(file):
    with open(file, 'rb') as f:
        content = pickle.load(f)
    return content


def write(file, content):
    with open(file, 'wb') as f:
        pickle.dump(content, f)


def test_read_datfile():
    file_name = "data/file.dat"
    tested_dict = dict(zip([key for key in random.choices(string.ascii_letters, k=10)],
                            [val for val in random.choices(string.ascii_letters, k=10)]))
    write(file_name, tested_dict)
    assert dat_files.read_file(file_name) == tested_dict


def test_write_datfile():
    file_name = "data/file.dat"
    tested_dict = dict(zip([key for key in random.choices(string.ascii_letters, k=10)],
                            [val for val in random.choices(string.ascii_letters, k=10)]))   
    if os.path.exists(file_name):
        os.remove(file_name)
    assert os.path.exists(file_name) is False
    dat_files.write_file(file_name, tested_dict)
    assert os.path.exists(file_name) is True






