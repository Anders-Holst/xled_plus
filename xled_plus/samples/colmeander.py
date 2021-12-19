from .sample_setup import *

ctr = setup_control()
oldmode = ctr.get_mode()["mode"]
eff = ColorMeanderEffect(ctr, "solid")
eff.launch_rt()
print("Started continuous effect - press Return to stop it")
input()
eff.stop_rt()
ctr.set_mode(oldmode)
