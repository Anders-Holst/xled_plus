"""
Day 25 - Random walk in color space

Solid color that slowly changes randomly.
This is a continuous effect, not a movie, so when you stop the script
the effect stops. 
"""

from xled_plus.samples.sample_setup import *

ctr = setup_control()
oldmode = ctr.get_mode()["mode"]
eff = ColorMeanderEffect(ctr, "solid")
eff.launch_rt()
print("Started continuous effect - press Return to stop it")
input()
eff.stop_rt()
ctr.set_mode(oldmode)
