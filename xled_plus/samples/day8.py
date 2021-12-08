"""
Day 8 - Flash with pair of slowly changing colors

Sparkling effect, starting with a flash and fading out, just like Day6,
but now with two simultaneous colors, slowly traversing the spectrum. 
"""

from xled_plus.samples.sample_setup import *

ctr = setup_control()
eff = SparkleEffect(ctr, 4, circular_color_func(240, [0.0, 0.25]), flashlight_func(16, 16))
eff.preferred_frames = 240
eff.launch_movie()
