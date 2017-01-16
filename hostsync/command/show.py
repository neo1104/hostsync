from hostsync.client import zk
from hostsync import utils
from hostsync.configure import HostsyncConfigure
import sys

def show():
    if len(sys.argv) != 2:
        print('usage: hostsync.py show')
        return
    zk.start()
    zoo_hosts = zk.get_children(HostsyncConfigure.HOSTS_LIST_NODE)
    for host in zoo_hosts:
        node_path = node_path = HostsyncConfigure.HOSTS_LIST_NODE + '/' + host
        (value, state) = zk.get(node_path)
        s = utils.str_to_list(value.decode('utf-8'))
        print("%s:%s" % (host, s))
    zk.stop()
