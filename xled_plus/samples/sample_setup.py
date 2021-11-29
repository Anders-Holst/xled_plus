from xled.discover import discover
from xled_plus.highcontrol import HighControlInterface
from xled_plus.ledcolor import *
from xled_plus.pattern import *
from xled_plus.effects import *
from xled_plus.sequence import *
from xled_plus.shapes import *
from sys import argv

def setup_control():
    if len(argv) > 1:
        host = argv[1]
    else:
        dev = discover()
        host = dev.ip_address
    return HighControlInterface(host)


