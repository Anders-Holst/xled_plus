"""
Day 11 - Gradients of yellow

Gradients of yellow, green and orange sweeping diagonally over the lights.
Uses the layout, and for best effect you may have to adjust the aspect ratio:
The parameter to adjust_layout_aspect should be set to width/height of the lights.
"""

from xled_plus.samples.sample_setup import *

ctr = setup_control()
ctr.adjust_layout_aspect(1.0)  # How many times wider than high is the led installation?
cols = [hsl_color(0.375, 0.2, 0.0), hsl_color(0.375, 1.0, 0.0), hsl_color(0.28, 1.0, 0.0), hsl_color(0.375, 0.2, 0.0), hsl_color(0.375, 1.0, 0.0), hsl_color(0.5, 1.0, 0.0)]
GradientSequence(ctr, cols, speed=0.04, folds=0.5, angle=45).launch_movie()
