from xled.discover import xdiscover
from xled.control import ControlInterface
from xled.exceptions import DiscoverTimeout

def discover_all():
    dd = xdiscover(timeout=3.0)
    lst = []
    while True:
        try:
            lst.append(next(dd))
        except DiscoverTimeout:
            return lst

def checksyncmode(ip):
    ctr = ControlInterface(ip)
    name = ctr.get_device_name()['name']
    sync = ctr.get_led_movie_config()['sync']
    if sync['mode'] == 'master':
        uid = sync['master_id'] if 'master_id' in sync else sync['uid'] if 'uid' in sync else False
    elif sync['mode'] == 'slave':
        uid = sync['slave_id'] if 'slave_id' in sync else sync['uid'] if 'uid' in sync else False
    else:
        uid = False
    return (name, sync['mode'], uid)

def controldict(devlst):
    dic = {}
    for dev in devlst:
        ip = dev.ip_address
        (name, mode, uid) = checksyncmode(ip)
        if uid and uid not in dic:
            dic[uid] = []
        if mode == 'master':
            dic[uid].insert(0, ip)
        elif mode == 'slave':
            dic[uid].append(ip)
        else:
            dic[name] = [ip]
    return dic


            
            
