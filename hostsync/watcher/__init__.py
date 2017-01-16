from hostsync.configure import HostsyncConfigure
from hostsync.client import zk
from kazoo.protocol.states import EventType
from hostsync.client import child_nodes
from hostsync import hosts
from hostsync import utils
import logging

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
            hosts.update_hosts(node, utils.str_to_list(value.decode('utf-8')))
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
                hosts.update_hosts(node, utils.str_to_list(value.decode('utf-8')))
