import socket


def hostname_to_ips(domain):
    try:
        addr_info = socket.gethostbyname_ex(domain)
    except socket.gaierror:
        raise ValueError("EXCEPTION ERROR: can not resolve {}".format(domain))
    else:
        ips = addr_info[2]
        if ips == []:
            raise ValueError("EXCEPTION ERROR: can not resolve {}, got empty alias list".format(domain))
        return sorted(ips)
