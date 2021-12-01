"""
Day 2 - Water

Bluish, greenish and white, like glittering water in a pond.
Similar to what can be achieved by the Glow effect in the app, but
colors change instead of just pulsing, and the transition to the first
frame is smooth, rather than with that annoying glitch you get with
the effect in the app.
"""

from xled_plus.samples.sample_setup import *

ctr = setup_control()
Water(ctr).launch_movie()
