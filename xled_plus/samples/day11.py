"""
Day 11 - Gradients of yellow


"""

from xled_plus.samples.sample_setup import *

ctr = setup_control()
cols = [hsl_color(0.375, 0.2, 0.0), hsl_color(0.375, 1.0, 0.0), hsl_color(0.28, 1.0, 0.0), hsl_color(0.375, 0.2, 0.0), hsl_color(0.375, 1.0, 0.0), hsl_color(0.5, 1.0, 0.0)]
GradientSequence(ctr, cols, speed=0.04, folds=0.5, angle=45).launch_movie()
