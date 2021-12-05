"""
Day 6 - Flash with mixed colors

Light colors starting with a flash and then fading out.
"""

from xled_plus.samples.sample_setup import *

ctr = setup_control()
SparkleEffect(ctr, 4, random_color_func(light=0.2), flashlight_func(16, 16)).launch_movie()
