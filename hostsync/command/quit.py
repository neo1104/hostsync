import os, signal
from hostsync.configure import HostsyncConfigure

def quit():
    fs = open(HostsyncConfigure.PID_PATH, 'r')
    pid = int(fs.readline())
    fs.close()
    os.kill(pid, signal.SIGQUIT)
