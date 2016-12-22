class HostsyncConfigure:
    ZOO_SERVER = 'zoo1:2181,zoo2:2181,zoo3:2181'
    HOSTS_LIST_NODE = '/hostsync'
    #HOST_FILE_PATH = '/etc/hosts'
    HOST_FILE_PATH = '/Users/neo/Documents/GitHub/hostsync/test/hosts'
    PID_PATH = '/var/run/hostsync.pid'
    LOG_PATH = '/var/log/hostsync.log'
    HOSTS_FILE_BGEIN = "####BEGIN HOSTSYNC GENERATED, DON'T MANUAL MODIFIED####"
    HOSTS_FILE_END = "####END HOSTSYNC GENERATED, DON'T MANUAL MODIFIED####"
