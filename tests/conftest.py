def pytest_addoption(parser):
    parser.addoption("--dont_skip_real", action="store_true", help="\
                     don't skip tests that need to communicate with the outside world (nslookup, sendmail etc.)")
