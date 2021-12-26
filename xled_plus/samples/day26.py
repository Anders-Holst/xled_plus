"""
Day 26 - Random walk with complementary colors

Variant of the Day 25 effect, with a gradient between a random walk
color and its complement. 
This is again a continuous effect, not a movie, so when you stop the script
the effect stops. 
"""

from xled_plus.samples.sample_setup import *

ctr = setup_control()
oldmode = ctr.get_mode()["mode"]
eff = MeanderingTandemSequence(ctr, gap=0.5, fixangle=0.0)
eff.launch_rt()
print("Started continuous effect - press Return to stop it")
input()
eff.stop_rt()
ctr.set_mode(oldmode)
