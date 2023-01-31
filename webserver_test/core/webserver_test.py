import asyncio
from ..utils import dataset as ds
from ..utils import send_requests as send_req
import time


REQUEST_STNGS = {
    "timeout": 10,
    "max_retries": 0
    }


class CommonWebSrvTest():
    def __init__(self, host_groups, services, rqst_stngs=None) -> None:
        print("# 0.\tInitialization...")
        self.host_groups = host_groups
        if rqst_stngs is None:
            self.rqst_stngs = REQUEST_STNGS
        else:
            self.rqst_stngs = rqst_stngs
        self.services = services
        if type(services) == list:
            self.services = dict.fromkeys(host_groups, services)
        self.hosts_df = None
        self.websrvtest_df = None
        self.dataset = None

    def _to_scv(self) -> None:
        if self.hosts_df is not None:
            self.hosts_df.to_csv("data/hosts.csv")
        if self.websrvtest_df is not None:
            self.websrvtest_df.to_csv("data/websrvtest_result.csv")
        if self.dataset is not None:
            self.dataset.to_csv("data/dataset.csv")

    def _data_compilation(self) -> None:
        print("# 1.1\tMaking hosts_dataframe...")
        self.hosts_df = ds.lookup_groups(self.host_groups)
        print("# 1.2\tMaking dataset from hosts_dataframe...")
        # hosts_df, {'customer_1.site.com': ["reports", "support"]}
        self.dataset = ds.make_dataset(self.hosts_df, self.services)

    def _run_websrvtest_tasks(self) -> None:
        print("# 2\tSending http requests...")
        initial_time = time.time()
        asynctask_results = asyncio.run(send_req.websrvtest_tasks(self.dataset, self.rqst_stngs))
        elapsed = time.time()-initial_time
        print("\tSending finished! Elapsed: {:.2f} sec".format(elapsed))
        self.websrvtest_df = ds.join_testresult_dataset(asynctask_results, self.dataset)
        self._to_scv()

    def _make_txt_summary(self) -> None:
        LITE_REPORT_COL = ['group_name', 'host_label', 'host_ip', 'service_name', 'status_code']
        self.txt_summary = {}
        if not self.errors.empty:
            errors_list = self.errors.loc[:, LITE_REPORT_COL].values.tolist()
            self.txt_summary["errors"] = "\n".join(["{}, {} ({}): {}, status_code {}".format(*items) for items in errors_list])
        if not self.no_errors.empty:
            no_errors_list = self.no_errors.loc[:, LITE_REPORT_COL].values.tolist()
            self.txt_summary["no_errors"] = "\n".join(["{}, {} ({}): {}, status_code {}".format(*items) for items in no_errors_list])
        res_list = self.websrvtest_df.loc[:, LITE_REPORT_COL].values.tolist()
        self.txt_summary["all"] = "\n".join(["{}, {} ({}): {}, status_code {}".format(*items) for items in res_list])

    def run(self):
        try:
            self._data_compilation()
        except ValueError as e:
            print(e)
            return {"all": "ERROR"}
        else:
            self._run_websrvtest_tasks()
            self.no_errors = self.websrvtest_df.query("status_code =='200'")
            self.errors = self.websrvtest_df.query("status_code !='200'")
            self._make_txt_summary()
            return self.txt_summary


if __name__ == '__main__':
    pass
