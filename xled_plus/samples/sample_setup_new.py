from xled_plus.highcontrol import HighControlInterface
from xled_plus.multicontrol import MultiHighControlInterface
from xled_plus.discoverall import *
from xled_plus.ledcolor import *
from xled_plus.pattern import *
from xled_plus.effects import *
from xled_plus.sequence import *
from xled_plus.shapes import *
from sys import argv
import re


def get_next_arg():
    if len(argv) > 1:
        return argv.pop(1)
    else:
        return False

def get_matching_arg(regexp):
    for i in range(1, len(argv)):
        if re.match(regexp, argv[i]):
            return argv.pop(i)
    return False

def print_devices(dic):
    print("Available devices:")
    for k in dic:
        print("  "+k+": "+ str(dic[k]))

def setup_control():
    """
    This function will try to create a HighControlInterface or
    MultiHighControlInterface for an available device or group
    of devices, using clues in the argument list to disambiguate
    which if there are several alternatives.
    In detail, if one or several ip-adresses are provided in the
    argument list when starting python, these are used as the devices.
    (If there are several, either all must be grouped together or
    none be grouped at all.)
    Otherwise the network is searched for all devices and groups of
    devices. If a single one is found, this is used. If several are
    found, the argument list is again searched, this time for the name
    of the device or group.
    Since this function is agressively chewing up the argument list,
    please chop off any other useful arguments first, with get_next_arg
    or get_matching_arg.
    """
    ips = []
    print("Arguments: " + str(argv))
    while True:
        arg = get_matching_arg("^([0-9]+)\.([0-9]+)\.([0-9]+)\.([0-9]+)$")
        if arg:
            ips.append(arg)
        else:
            break
    if ips:
        print("IP:s found: " + str(ips))
        if len(ips) > 1:
            ctr = MultiHighControlInterface(ips)
        else:
            ctr = HighControlInterface(ips[0])
    else:
        dic = controldict(discover_all())
        print_devices(dic)
        if not dic:
            print("No devices found")
            exit()
        dev = False
        print("Checking args " + str(argv[1:]))
        print("In keys " + str(dic.keys()))
        for arg in argv[1:]:
            if arg in dic:
                dev = arg
                argv.remove(arg)
                break
        if not dev:
            if len(dic) == 1:
                dev = list(dic.keys())[0]
            else:
                print_devices(dic)
                exit()
        if len(dic[dev]) > 1:
            ctr = MultiHighControlInterface(dic[dev])
        else:
            ctr = HighControlInterface(dic[dev][0])
    return ctr


