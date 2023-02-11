import pandas as pd
from io import StringIO
import asyncio
from .logs import WebServerLogs
from ...utils import dat_files as dat_files


LOG_COL = [
    'src_ip', 'server_protocol', 'time_local', 'request', 'status_code',
    'bytes_sent', 'http_user_agent', 'host_ip'
    ]

GREP_APP_LOGS_TAIL = "grep -hw {host} /var/log/nginx/access.log | tail -5"
SSH_TMPLT = 'ssh -o ConnectTimeout=5 -i {key} root@{host} "{cmd}"'


class CommonLogsCollector:
    def __init__(self, save_to=None):
        self.logs = None
        self.save_to = save_to

    async def _read_logs_by_ssh(self, cmd):
        proc = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await proc.communicate()
        if len(stdout) > 0:
            logs_df = pd.read_csv(StringIO(stdout.decode()), delimiter=' ', encoding='iso-8859-1', skipinitialspace=True, names=LOG_COL)
        else:
            logs_df = pd.DataFrame(columns=LOG_COL)
        return logs_df

    async def _readlogs_tasks(self, cmd_list):
        coroutines = [self._read_logs_by_ssh(cmd) for cmd in cmd_list]
        logs_list = await asyncio.gather(*coroutines)
        return logs_list

    def run(self, cmd_list):
        self.cmd_list = cmd_list
        self.logs_list = asyncio.run(self._readlogs_tasks(cmd_list))
        self.logs_list = list(enumerate(self.logs_list))
        self._save_logs(self.logs_list)
        return self.logs_list

    def _save_logs(self, logs):
        if self.save_to:
            dat_files.write_file(self.save_to, logs)


class LogsCollectorAfterTest(CommonLogsCollector):
    def __init__(self, save_to=None):
        super().__init__(save_to=save_to)

    def _make_readlog_cmds(self, hosts, key):
        cmd_list = []
        for ip in hosts:
            cmd = SSH_TMPLT.format(host=ip, key=key, cmd=GREP_APP_LOGS_TAIL.format(host=ip))
            cmd_list.append(cmd)
        return cmd_list

    def _data_compilation(self, wtest, with_errors_only=True):
        if with_errors_only:
            rqsts_with_errors = wtest.errors
            self.hosts = rqsts_with_errors.host_ip.unique()
        else:
            self.hosts = list(wtest.hosts_df.index)
        cmd_list = self._make_readlog_cmds(self.hosts, wtest.key)
        return cmd_list

    def run(self, wtest, **kwargs):
        self.read_logs_cmds = self._data_compilation(wtest, **kwargs)
        logs_list = asyncio.run(self._readlogs_tasks(self.read_logs_cmds))
        logs_list = list(enumerate(logs_list))
        logs = WebServerLogs(logs_list)
        if logs.raw != []:
            self.logs = logs
            self._save_logs(logs_list)
        else:
            self.logs = None
