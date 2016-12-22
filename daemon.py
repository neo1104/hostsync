import os, sys

def begin_daemon():
    pid = os.fork()
    if pid > 0:
        sys.exit(0)
    os.chdir('/')
    os.umask(0)
    os.setsid()
    pid = os.fork()
    if pid > 0:
        sys.exit(0)
