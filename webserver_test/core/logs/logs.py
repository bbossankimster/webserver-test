COL_TO_PRINT = ['time_local', 'host_ip', 'request', 'status_code']


class WebServerLogs:
    def __init__(self, logs_list) -> None:
        self.columns_to_print = COL_TO_PRINT
        self.raw = list(self._iter_logs(logs_list))

    def __repr__(self):
        if self.raw != []:
            logs_str_list = []
            for cntr, logs_df in self._iter_logs(self.raw):
                logs_str_list.append(logs_df[COL_TO_PRINT].to_string())
            return "\n\n".join(logs_str_list)
        else:
            return "Logs are empty"

    def _iter_logs(self, logs_list):
        for cntr, logs in logs_list:
            if not logs.empty:
                yield (cntr, logs)

    def to_html(self):
        if self.raw != []:
            logs_html = []
            for cntr, logs_df in self._iter_logs(self.raw):
                logs_html.append(logs_df[COL_TO_PRINT].to_html())
            return "".join(logs_html)
