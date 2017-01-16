from hostsync.configure import HostsyncConfigure
from hostsync.client import zk
import sys

def _zoo_push_hosts(hosts):
    zk.start()
    zk.ensure_path(HostsyncConfigure.HOSTS_LIST_NODE)
    zoo_hosts = zk.get_children(HostsyncConfigure.HOSTS_LIST_NODE)
    for host in hosts:
        for ip in host.keys():
            node_path = HostsyncConfigure.HOSTS_LIST_NODE + '/' + ip
            if ip not in zoo_hosts:
                zk.create(node_path, value=str(host[ip]).encode('utf-8'))
            else:
                zk.set(node_path, str(host[ip]).encode('utf-8'))
    print("hostsync: push down")
    zk.stop()

def push():
    if len(sys.argv) != 3 or not sys.argv[2]:
        print('usage: hostsync.py push <path_to_push_file>')
        return
    hosts = []
    fs = open(sys.argv[2])
    for line in fs.readlines():
        line = line.strip('\t\r\n')
        if line.startswith('#'):
            continue
        if len(line) <= 0:
            continue
        l = line.split()
        ip = l[0]
        if ip in ['127.0.0.1', 'localhost', '::1', '255.255.255.255']:
            continue;
        del l[0]
        for host in hosts:
            if ip in host.keys():
                for i in range(0, len(l)):
                    if l[i] in host[ip]:
                        continue
                    else:
                        host[ip].append(l[i])
                break
        else:
            host = {}
            host[ip] = []
            for i in range(0, len(l)):
                host[ip].append(l[i])
            hosts.append(host)
    fs.close()
    _zoo_push_hosts(hosts)
