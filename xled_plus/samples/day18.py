"""
Day 18 - Moving shapes

Colored geometric shapes moving over the leds.
Looks best on a 2D layout, and with correctly adjusted aspect: Change
the number in the call to adjust_layout_aspect in the code below.

I promised to not make just flashy but instead tasteful patterns.
This time maybe I failed, by trying to show a new kind of effect
just to prove it can be done, rather than for the estecics of it...
"""

from xled_plus.samples.sample_setup import *

ctr = setup_control()
ctr.adjust_layout_aspect(1.0)  # How many times wider than high is the led installation?
eff = MovingShapesScene(ctr)
eff.preferred_frames = 720
eff.launch_movie()
