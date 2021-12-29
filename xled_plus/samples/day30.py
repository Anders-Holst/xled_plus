"""
Day 30 - Random walk in colorspace with random gradient direction

Another variant of the Day 25 effect. Here the colors form a gradient that
moves over the leds at a slowly and randomly changing angle and change rate.
This is again a continuous effect. Aspect ratio is important as usual, so adjust below.
However, dimensionality or density of layout should matter less.
"""

from xled_plus.samples.sample_setup import *

ctr = setup_control()
ctr.adjust_layout_aspect(1.0)  # How many times wider than high is the led installation?
eff = MeanderingSequence(ctr)
oldmode = ctr.get_mode()["mode"]
eff.launch_rt()
print("Started continuous effect - press Return to stop it")
input()
eff.stop_rt()
ctr.set_mode(oldmode)
