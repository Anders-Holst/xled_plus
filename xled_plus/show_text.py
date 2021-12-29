from xled.discover import discover
from xled_plus.highcontrol import HighControlInterface
from xled_plus.ledcolor import *
from xled_plus.shapes import *
from sys import argv
import re

def isipaddress(txt):
    return re.match("([0-9]+)\.([0-9]+)\.([0-9]+)\.([0-9]+)", txt)

def makecolorlist(n):
    gs = (1.25**0.5 - 0.5)
    return [hsl_color((0.5 + gs * i) % 1.0, 1.0, 0.0) for i in range(n)]

if len(argv) == 3 and isipaddress(argv[1]):
    host = argv[1]
    txt = argv[2]
elif len(argv) == 3 and isipaddress(argv[2]):
    host = argv[2]
    txt = argv[1]
elif len(argv) == 2:
    txt = argv[1]
    host = discover().ip_address
else:
    print('Usage: python -m xled_plus.show_text [ip-address] "text"')
    quit()

ctr = HighControlInterface(host)
ctr.adjust_layout_aspect(1.0)
eff = RunningText(ctr, txt.upper(), makecolorlist(len(txt)), size=0.6, speed=0.5)
eff.launch_movie()
