from configure import HostsyncConfigure

def update_hosts(host, value, mode='update'):
    hostsync_block = []
    lineno = 0;
    found_begin = False
    found_end = False
    update = False
    fs = open(HostsyncConfigure.HOST_FILE_PATH, mode='r')
    lines = fs.readlines()
    for line in lines:
        lineno += 1
        if line.startswith(HostsyncConfigure.HOSTS_FILE_BGEIN):
            hostsync_block.append(HostsyncConfigure.HOSTS_FILE_BGEIN)
            found_begin = True
        elif line.startswith(HostsyncConfigure.HOSTS_FILE_END):
            if not update:
                if mode == 'update':
                    hostsync_block.append(host + ' ' + ' '.join(value))
                update = True
            hostsync_block.append(HostsyncConfigure.HOSTS_FILE_END)
            found_end = True
        elif found_begin and not found_end and line.startswith(host):
            if mode == 'update':
                hostsync_block.append(host + ' ' + ' '.join(value))
            update = True
        else:
            hostsync_block.append(line.strip())

    if not found_begin:
        if mode == 'update':
            hostsync_block.append(HostsyncConfigure.HOSTS_FILE_BGEIN)
            hostsync_block.append(host + ' ' + ' '.join(value))
            hostsync_block.append(HostsyncConfigure.HOSTS_FILE_END)

    fs.close()
    print('\n'.join(hostsync_block))
    fs = open(HostsyncConfigure.HOST_FILE_PATH, mode='w')
    fs.write('\n'.join(hostsync_block))
    fs.close()
