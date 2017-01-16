from hostsync.configure import HostsyncConfigure
from hostsync.command.help import help
from hostsync.command import commands
import sys, os, signal
import logging

def main():
    if len(sys.argv) < 2:
        help()
        exit(0)
    found = False
    for dict in commands:
        if dict['command'] == sys.argv[1]:
            found = True
            dict['proc']()
    if not found:
        print('unknown command %s, exists' % sys.argv[1])

if __name__ == '__main__':
    main()
