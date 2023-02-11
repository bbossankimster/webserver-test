import argparse
from webserver_test import CommonWebSrvTest, WebSrvTestWithLogs, WebSrvTestWithAlerts, WtestSettings
import time


class AppsAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if values == 'all':
            setattr(namespace, self.dest, self.default.split(","))
        elif values is not None:
            setattr(namespace, self.dest, values.split(","))


def add_arguments(parser, conf):
    parser.add_argument('mode', type=str, choices=['simple', 'with_logs_gathering', 'with_alerts_sending'])
    parser.add_argument('-d', '--host_domains', default="example1.site.com", type=str, help='separated by commas, example: -d example1.site.com,example2.site.com')
    parser.add_argument('-a', '--web_applications', action=AppsAction, default=conf.services, type=str, help='separated by commas, example: -a reports,support,analytics')
    parser.add_argument('-t', '--err_threshold', default=10, type=float, help='errors threshold (%) for services, example: -t 15')
    # mail alerts options
    parser.add_argument('-e', '--send_errors_to', default=conf.send_to_errors, type=str, help='send errors report to, example: -e andrey@example.com')
    parser.add_argument('-n', '--send_no_errors_to', default=conf.send_to_no_errors, type=str, help='send no_errors report to, example: -n no_errors@example.com')
    parser.add_argument('-u', '--update_settings', action="store_true", help='update default settings from input')


def print_results_common(wtest):
    if wtest.txt_summary["all"] != "ERROR":
        print("\nСписок серверов, которые участвуют в тесте:", wtest.hosts_df, sep="\n")
        print("\nРезультаты теста")
        if wtest.txt_summary.get('errors'):
            print("\n>>> HTTP запросы, завершенные с ошибкой:", wtest.txt_summary['errors'], sep="\n\n")
        if wtest.txt_summary.get('no_errors'):
            print("\n>>> HTTP запросы, завершенные без ошибок:", wtest.txt_summary['no_errors'], sep="\n\n")
        if wtest.findings:
            print("\n\n>>> Анализ результатов теста...", wtest.findings, sep="\n\n")


def print_results_extended(test_mode, wtest, error_code):
    if test_mode != "simple":
        if wtest.logs:
            print("\n>>> Логи веб серверов:", wtest.logs, sep="\n")
        else:
            print("\n>>> Не удалось собрать логи веб серверов!", sep="\n")
    if test_mode == "with_alerts_sending":
        if error_code:
            print(">>>", error_code)
        else:
            print("\n>>> Отчет отправлен по email! ({}, {})".format(args.send_errors_to, args.send_no_errors_to))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='\n\nWebserver test!\n')
    conf = WtestSettings("wtest.conf")
    add_arguments(parser, conf)
    args = parser.parse_args()
    if args.update_settings:
        conf.input_from_console()
    if not conf.is_default:
        apps = args.web_applications
        domains = args.host_domains.split(",")
        err_threshold = args.err_threshold
        initial_time = time.time()
        if args.mode == "simple":
            wtest = CommonWebSrvTest(domains, apps)
        elif args.mode == "with_logs_gathering":
            wtest = WebSrvTestWithLogs(domains, apps, key=conf.ssh_key_path, err_threshold=err_threshold)
        else:
            wtest = WebSrvTestWithAlerts(domains, apps, key=conf.ssh_key_path, err_threshold=err_threshold)
        wtest.run()
        if args.mode == "with_alerts_sending":
            to_string = args.send_errors_to + ";" + args.send_no_errors_to
            error_code = wtest.sendmail(conf.auth, to_string, "#webserver_test")
        print_results_common(wtest)
        print_results_extended(args.mode, wtest, error_code)
        print("\n>>> Тест выполнен за {:.2f} секунд".format(time.time()-initial_time))
    else:
        print("\nDefault settings found!\nExecute command with '-u' option or edit '{}' manually!\n".format(conf.config_path))