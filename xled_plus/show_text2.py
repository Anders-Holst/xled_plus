# usage: python -m show_text <text> <aspect_ratio> <name_of_device>

from xled_plus.discoverall import *
from xled_plus.highcontrol import HighControlInterface
from xled_plus.multicontrol import MultiHighControlInterface
from xled_plus.ledcolor import *
from xled_plus.shapes import *
from sys import argv
import re

def isipaddress(txt):
    return re.match("([0-9]+)\.([0-9]+)\.([0-9]+)\.([0-9]+)", txt)

def makecolorlist(n):
    gs = (1.25**0.5 - 0.5)
    return [hsl_color((0.5 + gs * i) % 1.0, 1.0, 0.0) for i in range(n)]

if len(argv) == 1:
    print("Usage: python -m xled_plus.show_text <text> [<aspect_ratio>] [<device_name_or_ip>]")
    exit()

if len(argv) == 4:
    if isipaddress(argv[3]):
        iplst = [argv[3]]
    else:
        devdict = controldict(discover_all())
        if argv[3] in devdict:
            iplst = devdict[argv[3]]
        else:
            print("No such Twinkly device detected: %s" % (argv[3]))
            exit()
else:
    devdict = controldict(discover_all())
    if len(devdict.keys()) == 1:
        iplst = devdict[list(devdict.keys())[0]]
    else:
        print("Multiple Twinkly devices detected: " + str(list(devdict.keys())))
        exit()

if len(argv) >= 3:
    aspect = float(argv[2])
else:
    aspect = 1.0

txt = argv[1]

if len(iplst) == 1:
    ctr = HighControlInterface(iplst[0])
else:
    ctr = MultiHighControlInterface(iplst)

ctr.adjust_layout_aspect(aspect)
eff = RunningText(ctr, txt.upper(), makecolorlist(len(txt)), size=0.6, speed=0.5)
eff.launch_movie()
