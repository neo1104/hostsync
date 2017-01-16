from kazoo.protocol.states import WatchedEvent
from kazoo.protocol.states import EventType
from kazoo.protocol.states import KazooState
from kazoo.protocol.states import KeeperState
from hostsync.client import zk
from hostsync import client
from hostsync.client import child_nodes
from hostsync.configure import HostsyncConfigure
from hostsync import server
import logging, os, time
from hostsync import watcher

def daemon():
    if HostsyncConfigure.IS_DAEMON:
        if os.path.exists(HostsyncConfigure.PID_PATH):
            print("%s exists" % HostsyncConfigure.PID_PATH)
            return;
        server.init()
        logging.basicConfig(filename=HostsyncConfigure.LOG_PATH, level=HostsyncConfigure.LOG_LEVEL, format=HostsyncConfigure.LOG_FORMATER)
    else:
        logging.basicConfig(level=HostsyncConfigure.LOG_LEVEL, format=HostsyncConfigure.LOG_FORMATER)
    logger = logging.getLogger(__name__)
    logger.info('Connected Zookeeper Server %s', HostsyncConfigure.ZOO_SERVER)
    zk.start()
    logger.info('Get Children of %s', HostsyncConfigure.HOSTS_LIST_NODE)
    watcher.hostsync_root_watcher(WatchedEvent(type=EventType.CHILD, state=KeeperState.CONNECTED, path=HostsyncConfigure.HOSTS_LIST_NODE))

    while True:
        time.sleep(1)
        logger.debug('time alarm, HOSTSYNC_QUIT:%s', client.get_hostsync_quit())
        if client.get_hostsync_quit():
            zk.stop()
            zk.close()
            os.remove(HostsyncConfigure.PID_PATH)
            exit(0)
        elif client.get_hostsync_status() != 'CONNECTED':
            if zk.state == KazooState.CONNECTED:
                child_nodes.clear()
                watcher.hostsync_root_watcher(WatchedEvent(type=EventType.CHILD, state=KeeperState.CONNECTED, path=HostsyncConfigure.HOSTS_LIST_NODE))
                client.set_hostsync_status('CONNECTED')
