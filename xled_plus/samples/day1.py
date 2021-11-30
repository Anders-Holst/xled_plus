"""
Day 1 - Twinkling stars

A simple effect to start with. It is similar to the Star effect in the
Twinkly app. However, in the app all stars have the same purple-tinted
sharp white color ("Twinkly-white"). Here instead the stars have
different color temperatures, from warm, through neutral white to cold
- just like real stars.
"""

from xled_plus.samples.sample_setup import *

ctr = setup_control()
SparkleStars(ctr).launch_movie()
