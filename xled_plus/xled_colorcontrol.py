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
from xled_plus.samples.sample_setup import *

def TwinkleFunc(ctr, cols):
    if cols:
        colsrgb = list(map(lambda hsl: hsl_color(*hsl), cols))
        eff = SparkleEffect(ctr, 3, selected_color_func(colsrgb), pulselight_func(16, 8, 16))
        eff.preferred_fps = 12
        return eff
    else:
        return False

def SparkleFunc(ctr, cols):
    if cols:
        colsrgb = list(map(lambda hsl: hsl_color(*hsl), cols))
        eff = SparkleEffect(ctr, 4, selected_color_func(colsrgb), flashlight_func(16, 16))
        eff.preferred_fps = 12
        return eff
    else:
        return False

def BreatheFunc(ctr, cols):
    if cols:
        return BreathCP(ctr, cols)
    else:
        return False

def GlowFunc(ctr, cols):
    if len(cols) >= 2:
        return GlowCP(ctr, cols)
    else:
        return False

def GlitterFunc(ctr, cols):
    if cols:
        return GlitterCP(ctr, cols)
    else:
        return False

def SequenceFunc(ctr, cols):
    if len(cols) >= 2:
        colsrgb = list(map(lambda hsl: hsl_color(*hsl), cols))
        eff = GradientSequence(ctr, colsrgb, speed=0.02, folds=0.0, angle=0)
        return eff
    else:
        return False

def BandFunc(ctr, cols):
    if len(cols) >= 2:
        colsrgb = list(map(lambda hsl: hsl_color(*hsl), cols))
        eff = GradientSequence(ctr, colsrgb, speed=0.02, folds=0.25, angle=0)
        return eff
    else:
        return False


if __name__ == '__main__':

    efflist = [("Breathe", BreatheFunc),
               ("Glow", GlowFunc),
               ("Twinkle", TwinkleFunc),
               ("Sparkle", SparkleFunc),
               ("Glitter", GlitterFunc),
               ("Sequence", SequenceFunc),
               ("Bands", BandFunc)]

    ctr = setup_control()

    cc = ColorControl(ctr, efflist)
    cc.start_event_loop()
