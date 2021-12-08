"""
Day 9 - Pulselights green

Smoothly pulsing lights with random colors from the green spectrum.
"""

from xled_plus.samples.sample_setup import *

ctr = setup_control()
colfunc = random_color_func(hue=[0.16, 0.38], light=0.0)
nsparks = 0.5 * ctr.num_leds / 60.0
eff = SparkleEffect(ctr, nsparks, colfunc, pulselight_func(24, 12, 24))
eff.preferred_fps = 12
eff.preferred_frames = 180
eff.launch_movie()
