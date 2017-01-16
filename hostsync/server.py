import os, sys
import signal
import logging
from hostsync.configure import HostsyncConfigure
from hostsync import client


def _sigquit_handler(signum, frame):
    logger = logging.getLogger(__name__)
    client.set_hostsync_quit(True)
    logger.debug("set HOSTSYNC_QUIT to %s", client.get_hostsync_quit())

def init():
    pid = os.fork()
    if pid > 0:
        sys.exit(0)
    os.umask(0)
    os.setsid()
    pid = os.fork()
    if pid > 0:
        sys.exit(0)

    pid = os.getpid()
    # create pid file
    fs = open(HostsyncConfigure.PID_PATH, 'w')
    fs.write(str(pid))
    fs.close()

    # set signal handler
    signal.signal(signal.SIGQUIT, _sigquit_handler)
