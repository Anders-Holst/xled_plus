"""
Day 4 - White tinted gradient

Slowly changing gradient between two complementary light colors,
such that the middle stays white and the colors above and below
traverses the spectrum on opposite sides.

This effect uses the physical layout of the leds. It only uses
one coordinate though (y-axis), so it should work for 2D, 3D, or
linear layouts. (Older firmware do not store the layout on the leds.
For them the effect will follow the string instead.)
"""

from xled_plus.samples.sample_setup import *

def tintedwhite(t, pos):
    y = pos[1] if len(pos) > 1 else pos[0]
    return hsl_color(t%1.0 if y<0.5 else (t + 0.5)%1.0, 1.0, 1.0 - abs(y - 0.5)*1.6)

ctr = setup_control()
mov = ctr.make_func_movie(120, lambda t: ctr.make_layout_pattern(lambda pos: tintedwhite(t / 120.0, pos)))
ctr.show_movie(mov, 0.5)
