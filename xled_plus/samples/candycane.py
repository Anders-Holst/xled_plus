"""
Day 11 mod: Candy Cane
Daily effect, December 11 Modified to resemble a Candy Cane pattern

Red and white sweeping diagonally over the lights.

Contributed by gonzotek
"""

from xled_plus.samples.sample_setup import *

ctr = setup_control()
ctr.set_mode("off")

ctr.adjust_layout_aspect(1.0)  # How many times wider than high is the led installation?
cols = [hsl_color(0.6226, 1.0, -0.5631), hsl_color(0.6226, 1.0, -0.5631), hsl_color(0.5830, 1.0000, 0.5121), hsl_color(0.6226, 1.0, -0.5631), hsl_color(0.6226, 1.0, -0.5631), hsl_color(0.5830, 1.0000, 0.5121), hsl_color(0.6226, 1.0, -0.5631), hsl_color(0.6226, 1.0, -0.5631), hsl_color(0.5830, 1.0000, 0.5121), hsl_color(0.6030, 1.0000, 0.2121)]
GradientSequence(ctr, cols, speed=0.05, folds=0.8, angle=25).launch_movie()
