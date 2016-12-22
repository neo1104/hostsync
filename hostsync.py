from kazoo.client import KazooClient
from kazoo.client import KazooState
from kazoo.protocol.states import EventType
from kazoo.protocol.states import KeeperState
from kazoo.protocol.states import WatchedEvent
from configure import HostsyncConfigure
from daemon import begin_daemon
import watcher
from update_hosts import update_hosts
import sys, time

zk = KazooClient(hosts=HostsyncConfigure.ZOO_SERVER)
child_nodes = []

def str_to_list(s):
    l = []
    tmp = s.strip('[]').split(',')
    for i in tmp:
        l.append(i.strip().strip("'"))
    return l

def hostsync_node_watcher(event):
    print(event)
    node = event.path[len(HostsyncConfigure.HOSTS_LIST_NODE + '/'):len(event.path)]
    if event.type == EventType.DELETED:
        child_nodes.remove(node)
        update_hosts(node, None, mode='delete')
    elif event.type == EventType.CREATED:
        pass
    elif event.type == EventType.CHANGED:
        #get changed value and re register node watcher
        (value, state) = zk.get(event.path, watch=hostsync_node_watcher)
        if (len(value) >= 0):
            update_hosts(node, str_to_list(value.decode('utf-8')))
    else:
        pass

def hostsync_root_watcher(event):
    # get node list and re register watcher
    print(event)
    nodes = zk.get_children(HostsyncConfigure.HOSTS_LIST_NODE, watch=hostsync_root_watcher)
    for node in nodes:
        if node not in child_nodes:
            child_nodes.append(node)
            # register watch for new created node
            (value, state) = zk.get(event.path + '/' + node, watch=hostsync_node_watcher)
            if (len(value) >= 0):
                update_hosts(node, str_to_list(value.decode('utf-8')))

@zk.add_listener
def zk_listener(state):
    if state == KazooState.LOST:
        pass
    elif state == KazooState.SUSPENDED:
        pass
    else:
        pass

def hostsync_show():
    if len(sys.argv) != 2:
        print('usage: hostsync.py show')
        return
    zk.start()
    zoo_hosts = zk.get_children(HostsyncConfigure.HOSTS_LIST_NODE)
    for host in zoo_hosts:
        node_path = node_path = HostsyncConfigure.HOSTS_LIST_NODE + '/' + host
        (value, state) = zk.get(node_path)
        s = str_to_list(value.decode('utf-8'))
        print("%s:%s" % (host, s))
    zk.stop()

def zoo_push_hosts(hosts):
    zk.start()
    zk.ensure_path(HostsyncConfigure.HOSTS_LIST_NODE)
    zoo_hosts = zk.get_children(HostsyncConfigure.HOSTS_LIST_NODE)
    for host in hosts:
        for ip in host.keys():
            node_path = HostsyncConfigure.HOSTS_LIST_NODE + '/' + ip
            if ip not in zoo_hosts:
                zk.create(node_path, value=str(host[ip]).encode('utf-8'))
            else:
                (value, state) = zk.get(node_path)
                s = str_to_list(value.decode('utf-8'))
                update = False
                for i in host[ip]:
                    if i not in s:
                        update = True
                        s.append(i)
                if update:
                    zk.set(node_path, str(s).encode('utf-8'))
    print("hostsync: push down")
    zk.stop()

def hostsync_push():
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
    zoo_push_hosts(hosts)


def hostsync_help():
    print('''
Usage: hostsync.py <COAMMND> [COMMAND-OPTIONS]
COMMANDS:
 help
 show
 push
 daemon
          ''')
    exit(0)

def hostsync_daemon():
    #begin_daemon()
    zk.start()
    hostsync_root_watcher(WatchedEvent(type=EventType.CHILD, state=KeeperState.CONNECTED, path=HostsyncConfigure.HOSTS_LIST_NODE))
    while True:
        time.sleep(1)


commands = [
            {
                'command': 'push',
                'proc': hostsync_push
            },
            {
                'command': 'help',
                'proc': hostsync_help
            },
            {
                'command': 'show',
                'proc': hostsync_show
            },
            {
                'command': 'daemon',
                'proc': hostsync_daemon
            }
]

def hostsysnc_command():
    if len(sys.argv) < 2:
        hostsync_help()
        exit(0)
    found = False
    for dict in commands:
        if dict['command'] == sys.argv[1]:
            found = True
            dict['proc']()
    if not found:
        print('unknown command %s, exists' % sys.argv[1])

if __name__ == '__main__':
    hostsysnc_command()
