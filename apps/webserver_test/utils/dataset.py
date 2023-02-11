from .hostnames import hostname_to_ips
from netaddr import IPAddress, AddrFormatError
import pandas as pd

URL_TMPLT = 'http://{ip}:{port}/{page}'
HOSTS_COL = ["group_type", "group_name", "id", "id_in_group", "host_label", "host_ip"]
PORTS = {
    "reports": "8001",
    "support": "8002",
    "analytics": "8004",
    "store": "8004"
}


def make_dataset(hosts_df, services: dict):
    server_data_list = []
    for host_index in hosts_df.index:
        server_data = hosts_df.loc[host_index]
        grp_name = server_data['group_name']
        for service in services[grp_name]:
            server_data_mod = server_data.copy()
            server_data_mod['url'] = URL_TMPLT.format(port=PORTS[service], ip=server_data['host_ip'], page=service+".html")
            server_data_mod['service_name'] = service
            server_data_list.append(server_data_mod)
    dataset = pd.DataFrame(server_data_list).reset_index(drop=True)
    # dataset = dataset.set_index(["row_id"], drop=True)
    return dataset


def lookup_groups(host_groups):
    hosts_count = 0
    host_list = []
    for host_grp in host_groups:
        try:
            ip = IPAddress(host_grp)
        except AddrFormatError:
            if host_grp == "customer_1.site.com":
                ips = ['192.168.100.8', '192.168.100.9']
            else:
                ips = hostname_to_ips(host_grp)
            ips = [['domain', host_grp, id+hosts_count, id, "server {}".format(id), ips[id-1]] for id in range(1, len(ips)+1)]
            hosts_count = hosts_count + len(ips)
            host_list = host_list + ips
        else:
            hosts_count += 1
            host_list = host_list + [['ip', host_grp, hosts_count, 1, "server 1", host_grp]]
    if host_list == []:
        host_list = [[]]
    df = pd.DataFrame(host_list, columns=HOSTS_COL).set_index(["id"], drop=True)
    return df


def join_testresult_dataset(results, dataset):
    data_list = []
    cntr = -1
    for index in dataset.index:
        cntr +=1
        status_code, resp_out, exception_request, tries = results[cntr]
        data = dataset.loc[index].copy()
        data['status_code'] = status_code
        data['resp_out'] = resp_out
        data['exception_request'] = exception_request
        data['tries'] = tries
        data['row_id'] = int(index)
        data_list.append(data)
    testresult_df = pd.DataFrame(data_list)
    return testresult_df
