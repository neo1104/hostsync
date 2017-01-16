from kazoo.client import KazooClient
from kazoo.protocol.states import KazooState
from hostsync.configure import HostsyncConfigure
import logging

_HOSTSYNC_QUIT = False
_HOSTSYNC_STATUS = 'CONNECTED'
zk = KazooClient(hosts=HostsyncConfigure.ZOO_SERVER)
child_nodes = []


def get_hostsync_quit():
    return _HOSTSYNC_QUIT

def set_hostsync_quit(v):
    global _HOSTSYNC_QUIT
    _HOSTSYNC_QUIT = v

def get_hostsync_status():
    return _HOSTSYNC_STATUS

def set_hostsync_status(v):
    global _HOSTSYNC_STATUS
    _HOSTSYNC_STATUS = v

@zk.add_listener
def zk_listener(state):
    global _HOSTSYNC_STATUS
    logger = logging.getLogger(__name__)
    if state == KazooState.LOST:
        logger.info("zookeeper connection LOST:[%s]", state)
        _HOSTSYNC_STATUS = 'LOST'
    elif state == KazooState.SUSPENDED:
        logger.info("zookeeper connection SUSPENDED:[%s]", state)
        _HOSTSYNC_STATUS = 'SUSPENDED'
    else:
        logger.info("zookeeper connection CONNECTED:[%s]", state)
