import os, sys
import signal
import logging
from configure import HostsyncConfigure

def begin_daemon():
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
