"""
Day 16 - Looping lights, blue, purple, orange

Same principle as yesterday with different colors.
Because I think it looks nice.
"""

from xled_plus.samples.sample_setup import *

ctr = setup_control()
nsparks = 0.4 * ctr.num_leds / 32.0
colfunc = selected_color_func([(0.9, 1.0), (0.1, 1.0), (0.5, 1.0)])
SparkleEffect(ctr, nsparks, colfunc, looplight_func(16, 16)).launch_movie()
