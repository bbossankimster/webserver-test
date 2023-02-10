from webserver_test import WtestSettings


stngs = WtestSettings("wtest.conf")
print(stngs.auth)
print(stngs.send_to_errors)
print(stngs.send_to_no_errors)
print(stngs.services)
