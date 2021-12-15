"""
Day 14 - Looping lights, red, magenta, green

Another variant of SparkleEffect, this time each led "looping" from black
through one of the selected colors to white, and then dims back to black
again (through gray). Gives nice white mix among the pulsating colors.
"""

from xled_plus.samples.sample_setup import *

ctr = setup_control()
nsparks = 0.4 * ctr.num_leds / 32.0
colfunc = selected_color_func([(0.6, 1.0), (0.7, 1.0), (0.28, 1.0)])
SparkleEffect(ctr, nsparks, colfunc, looplight_func(16, 16)).launch_movie()
