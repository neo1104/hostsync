from hostsync.command.daemon import daemon
from hostsync.command.help import help
from hostsync.command.push import push
from hostsync.command.quit import quit
from hostsync.command.show import show



commands = [
            {
                'command': 'push',
                'proc': push
            },
            {
                'command': 'help',
                'proc': help
            },
            {
                'command': 'show',
                'proc': show
            },
            {
                'command': 'quit',
                'proc': quit

            },
            {
                'command': 'daemon',
                'proc': daemon
            }
]
