"""
Day 5 - Dark to light colors

Gradient from dark to light of a slowly changing hue across the spectrum.

This effect uses the physical layout of the leds. It only uses
one coordinate though (y-axis), so it should work for 2D, 3D, or
linear layouts. (Older firmware do not store the layout on the leds.
For them the effect will follow the string instead.)
"""

from xled_plus.samples.sample_setup import *

def darklight(t, pos):
    light = pos[1] if len(pos) > 1 else pos[0]
    hue = t % 1.0
    return hsl_color(hue, 1.0, light*2 - 1)

ctr = setup_control()
mov = ctr.make_func_movie(120, lambda t: ctr.make_layout_pattern(lambda pos: darklight(t / 120.0, pos)))
ctr.show_movie(mov, 0.66)
