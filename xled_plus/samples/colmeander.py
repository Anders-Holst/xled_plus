from .sample_setup import *


ctr = setup_control()
eff = ColorMeanderEffect(ctr, "solid")
eff.launch_rt()
input()
eff.stop_rt()
ctr.turn_off()
