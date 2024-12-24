#!/usr/bin/python3

"""
xled_plus.xled_colorcontrol
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Author: Anders Holst (anders.holst@ri.se), 2024

Graphical user interface for creating, previewing and uploading
dynamic color effects to your led lights.

This is the main entrypoint. Run it with from the shell as
  python3 -m xled_plus.xled_colorcontrol

"""

from xled_plus.colorcontrol import *
from xled_plus.highcontrol import HighControlInterface
from xled_plus.multicontrol import MultiHighControlInterface
from xled_plus.discoverall import *
from xled_plus.ledcolor import *
from xled_plus.pattern import *
from xled_plus.effects import *
from xled_plus.sequence import *
from xled_plus.shapes import *


#   "Effect name": (effect class, min colors, min layout dimensions)
effect_dict = {
    "Breathe"  : (BreathCP, 1, 1),
    "Glow"     : (GlowCP, 2, 1),
    "Pulsate"  : (PulsateCP, 1, 1),
    "Sparkle"  : (SparkleCP, 1, 1),
    "Twinkle"  : (TwinkleCP, 1, 1),
    "Glitter"  : (GlitterCP, 1, 1),
    "Sequence" : (TimeSequenceCP, 2, 1),
    "Waves"    : (HorizontalWavesCP, 2, 1),
    "Bands"    : (HorizontalBandsCP, 2, 1)
}


def make_control_list():
    dic = controldict(discover_all())
    ctrlst = []
    for k in dic:
        if len(dic[k]) > 1:
            ctrlst.append(MultiHighControlInterface(dic[k]))
        else:
            ctrlst.append(HighControlInterface(dic[k][0]))
    return ctrlst


if __name__ == '__main__':

    cc = ColorControl(make_control_list(), effect_dict)
    cc.start_event_loop()
