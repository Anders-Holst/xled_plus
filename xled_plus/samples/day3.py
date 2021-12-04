"""
Day 3 - Gold

Similar to the Sparkles effect in the app, of bright flashing leds
against a solid background. This example is meant to mimic the
"metallic luster" effects of AWW leds, i.e glittering gold.
"""

from xled_plus.samples.sample_setup import *

ctr = setup_control()
Gold(ctr).launch_movie()
