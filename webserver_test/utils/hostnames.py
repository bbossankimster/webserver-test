import subprocess
import re
import platform


NSLOOKUP_TMPLT = "nslookup {} | grep Address | grep -v '#53'"
if platform.system() == "Linux":
    WIN_LINUX_SSH_TMPLT = r'{cmd}'
else:
    WIN_LINUX_SSH_TMPLT = r'cd C:\Users\1\Downloads\putty-0.73-ru-17-portable\PuTTY PORTABLE & plink netnut "{cmd}"'


def hostname_to_ips(host_domain):
    cmd = WIN_LINUX_SSH_TMPLT.format(cmd=NSLOOKUP_TMPLT.format(host_domain))
    exec = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, encoding='utf-8')
    out = exec.stdout
    err = exec.stderr
    ips = re.findall(r'\d+.\d+.\d+.\d+', out)
    if ips == []:
        raise ValueError("EXCEPTION ERROR: nslookup error for {}, out: {}, regexp_ips: {}".format(host_domain, out, ips))
    return sorted(ips)
