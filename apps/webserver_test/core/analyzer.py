ERR_HOSTS_DOWN = "Критическая ошибка!\n{} сервер(а) отключен(ы) и/или все приложения не работают\n{}\n------"
ERR_APPS_DOWN = "Критическая ошибка!\n{} Web-приложение(я) не работает(ют) на всех серверах:\n{}\n------"
ERR_APPS_EXCEEDING = "Внимание!\n{} Web-приложение(я) завершили тест с высоким уровнем ошибок:\n{}\n------"


class WtestAnalyzer:
    def __init__(self, rqsts_df, err_threshold=10) -> None:
        self.rqsts_df = rqsts_df.copy()
        self.err_threshold = err_threshold
        self.rqsts_without_hosts_down = None
        self.events_count = 0
        self.findings = []
        self.hosts_down = {}
        self.apps_down, self.apps_err_exceeding = {}, {}
        self._detect_hosts_down()
        self._detect_app_errors_exceeding()
        self.findings = [data for data in [self.hosts_down, self.apps_down, self.apps_err_exceeding] if data !={}]
        self.txt = self.__repr__()

    def _detect_hosts_down(self) -> None:
        hosts_down = {}
        hosts_err = self.rqsts_df.groupby(['group_name', 'host_label', 'host_ip'])["status_code"].agg(apps_with_errors=lambda x: (x != '200').sum(), apps_count="count")
        hosts_err_orig = hosts_err
        hosts_down_df = hosts_err[hosts_err["apps_count"] == hosts_err["apps_with_errors"]].reset_index()
        if not hosts_down_df.empty:
            ips = hosts_down_df["host_ip"].to_list()
            hosts_down["df"] = hosts_down_df
            hosts_down["hosts"] = ips
            hosts_down["hosts_err"] = hosts_err
            hosts_down["txt"] = ERR_HOSTS_DOWN.format(len(ips), "\n".join(ips))
            self.events_count += 1
            hosts_down_indx = self.rqsts_df.query("host_ip in {}".format(ips)).index
            self.rqsts_without_hosts_down = self.rqsts_df.drop(index=hosts_down_indx)
        self.hosts_down = hosts_down

    def _detect_app_errors_exceeding(self) -> None:
        apps_down = {}
        apps_err_exceeding = {}
        if self.rqsts_without_hosts_down is not None:
            rqsts_df = self.rqsts_without_hosts_down
        else:
            rqsts_df = self.rqsts_df
        err_threshold = self.err_threshold
        app_err = rqsts_df.groupby(['group_name', 'service_name'])["status_code"].agg(
            apps_count="count",
            apps_with_err_count=lambda x: (x != '200').sum(),
            status_list=lambda x: (x[x != '200']).unique())
        app_err["err_percentage"] = (app_err['apps_with_err_count'] / app_err['apps_count'] * 100).round(1)
        apps_down_df = app_err.query("err_percentage == 100").reset_index(drop=False)
        apps_err_exceeding_df = app_err.query("{} <= err_percentage < 100".format(err_threshold)).reset_index(drop=False)
        if not apps_down_df.empty:
            self.events_count += 1
            apps_names = apps_down_df["service_name"].to_list()
            apps_down["df"] = apps_down_df
            apps_down["names"] = apps_names
            apps_down["txt"] = ERR_APPS_DOWN.format(len(apps_names), "\n".join(sorted(apps_names)))
        if not apps_err_exceeding_df.empty:
            self.events_count += 1
            apps_names = apps_err_exceeding_df["app_name"].to_list()
            apps_err_exceeding["df"] = apps_err_exceeding_df
            apps_err_exceeding["names"] = apps_names
            apps_err_exceeding["txt"] = ERR_APPS_EXCEEDING.format(len(apps_names), "\n".join(sorted(apps_names)))
        self.apps_down, self.apps_err_exceeding = apps_down, apps_err_exceeding

    def __repr__(self):
        if self.events_count > 0:
            txt_list = [res["txt"] for res in self.findings]
            return "\n".join(txt_list)
        else:
            return "В ходе теста значительных оишбок не выявлено!"
