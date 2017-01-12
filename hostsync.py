from kazoo.client import KazooClient
from kazoo.client import KazooState
from kazoo.protocol.states import EventType
from kazoo.protocol.states import KeeperState
from kazoo.protocol.states import WatchedEvent
from configure import HostsyncConfigure
from daemon import begin_daemon
from update_hosts import update_hosts
import sys, time, os, signal
import logging

zk = KazooClient(hosts=HostsyncConfigure.ZOO_SERVER)
child_nodes = []

HOSTSYNC_QUIT = False
HOSTSYNC_STATUS = 'CONNECTED'

def sigquit_handler(signum, frame):
    global HOSTSYNC_QUIT
    logger = logging.getLogger(__name__)
    HOSTSYNC_QUIT = True
    logger.debug("set HOSTSYNC_QUIT to %s", HOSTSYNC_QUIT)

def str_to_list(s):
    l = []
    tmp = s.strip('[]').split(',')
    for i in tmp:
        l.append(i.strip().strip("'"))
    return l

def hostsync_node_watcher(event):
    logger = logging.getLogger(__name__)
    logger.info("receive %s node's %s event", event.path, event.type)
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
    logger = logging.getLogger(__name__)
    logger.info("receive %s node's %s event 1", event.path, event.type)
    nodes = zk.get_children(HostsyncConfigure.HOSTS_LIST_NODE, watch=hostsync_root_watcher)
    logger.info("receive %s node's %s event 2", event.path, event.type)
    for node in nodes:
        if node not in child_nodes:
            child_nodes.append(node)
            # register watch for new created node
            (value, state) = zk.get(event.path + '/' + node, watch=hostsync_node_watcher)
            logger.info("append new node:%s, value:%s", node, value)
            if (len(value) >= 0):
                update_hosts(node, str_to_list(value.decode('utf-8')))

@zk.add_listener
def zk_listener(state):
    global HOSTSYNC_STATUS
    logger = logging.getLogger(__name__)
    if state == KazooState.LOST:
        logger.info("zookeeper connection LOST:[%s]", state)
        HOSTSYNC_STATUS = 'LOST'
    elif state == KazooState.SUSPENDED:
        logger.info("zookeeper connection SUSPENDED:[%s]", state)
        HOSTSYNC_STATUS = 'SUSPENDED'
    else:
        logger.info("zookeeper connection CONNECTED:[%s]", state)

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
                zk.set(node_path, str(host[ip]).encode('utf-8'))
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

def hostsync_quit():
    fs = open(HostsyncConfigure.PID_PATH, 'r')
    pid = int(fs.readline())
    fs.close()
    os.kill(pid, signal.SIGQUIT)

def hostsync_daemon():
    global HOSTSYNC_STATUS
    if HostsyncConfigure.IS_DAEMON:
        if os.path.exists(HostsyncConfigure.PID_PATH):
            print("%s exists" % HostsyncConfigure.PID_PATH)
            return;
        begin_daemon()
        logging.basicConfig(filename=HostsyncConfigure.LOG_PATH, level=HostsyncConfigure.LOG_LEVEL, format=HostsyncConfigure.LOG_FORMATER)
        # set signal handler
        signal.signal(signal.SIGQUIT, sigquit_handler)
    else:
        logging.basicConfig(level=HostsyncConfigure.LOG_LEVEL, format=HostsyncConfigure.LOG_FORMATER)
    logger = logging.getLogger(__name__)
    logger.info('Connected Zookeeper Server %s', HostsyncConfigure.ZOO_SERVER)
    zk.start()
    logger.info('Get Children of %s', HostsyncConfigure.HOSTS_LIST_NODE)
    hostsync_root_watcher(WatchedEvent(type=EventType.CHILD, state=KeeperState.CONNECTED, path=HostsyncConfigure.HOSTS_LIST_NODE))
    while True:
        time.sleep(1)
        #logger.debug('time alarm, HOSTSYNC_QUIT:%s', HOSTSYNC_QUIT)
        if HOSTSYNC_QUIT:
            zk.stop()
            zk.close()
            os.remove(HostsyncConfigure.PID_PATH)
            exit(0)
        elif HOSTSYNC_STATUS != 'CONNECTED':
            if zk.state == KazooState.CONNECTED:
                child_nodes.clear()
                hostsync_root_watcher(WatchedEvent(type=EventType.CHILD, state=KeeperState.CONNECTED, path=HostsyncConfigure.HOSTS_LIST_NODE))
                HOSTSYNC_STATUS = 'CONNECTED'


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
                'command': 'quit',
                'proc': hostsync_quit

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
