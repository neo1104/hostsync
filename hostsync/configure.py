class HostsyncConfigure:
    IS_DAEMON = True
    ZOO_SERVER = '192.168.35.10:2181'
    HOSTS_LIST_NODE = '/hostsync'
    HOST_FILE_PATH = '/Users/neo/Documents/GitHub/hostsync/data/hosts'
    LOG_LEVEL = 'DEBUG'
    LOG_FORMATER = '%(asctime)-15s %(module)s:%(lineno)s %(levelname)s %(message)s'
    LOG_PATH = '/Users/neo/Documents/GitHub/hostsync/data/hostsync.log'
    PID_PATH = '/Users/neo/Documents/GitHub/hostsync/data/hostsync.pid'
    HOSTS_FILE_BGEIN = "####BEGIN HOSTSYNC GENERATED, DON'T MANUAL MODIFIED####"
    HOSTS_FILE_END = "####END HOSTSYNC GENERATED, DON'T MANUAL MODIFIED####"
