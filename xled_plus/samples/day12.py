"""
Day 12 - Gradients of blue

Gradients of blue, green and purple sweeping over the lights in rotating direction.
Uses the layout, and for best effect you may have to adjust the aspect ratio:
The parameter to adjust_layout_aspect should be set to width/height of the lights.
"""

from xled_plus.samples.sample_setup import *

ctr = setup_control()
ctr.adjust_layout_aspect(1.0)  # How many times wider than high is the led installation?
cols = [hsl_color(0.0, 0.0, 0.0),hsl_color(0.02, 1.0, 0.0), hsl_color(0.9, 1.0, 0.0), hsl_color(0.0, 0.0, 0.0), hsl_color(0.06, 1.0, 0.0), hsl_color(0.18, 1.0, 0.0)]
eff = RotatingAngleGradientSequence(ctr, cols, speed=0.04, folds=0.5, angle=-45, torque=7.2)
eff.preferred_frames = 400
eff.launch_movie()
