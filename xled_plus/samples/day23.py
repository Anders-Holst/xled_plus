"""
Day 23 - Crystal

Glittering white crystal, yet shimmering in all colors at once.
"""

from xled_plus.samples.sample_setup import *
from random import shuffle

class Crystal(RotateEffect):
    def __init__(self, ctr):
        saturations = [0.4, 0.0, 0.0, 0.2, 0.0, 0.0]
        folds = len(saturations)
        nleds = ctr.num_leds
        pat = ctr.make_func_pattern(
            lambda i: hsl_color((i*folds / float(nleds))%1.0, saturations[i*folds // nleds], 0.0),
            circular=True,
        )
        perm = list(range(nleds))
        shuffle(perm)
        self.nsparks = 0.02 * nleds
        self.white = hsl_color(0.0, 0.0, 1.0)
        self.preferred_fps = 12
        super(Crystal, self).__init__(ctr, pat, perm, step=2)

    def getnext(self):
        pat1 = super(Crystal, self).getnext()
        return sprinkle_pattern(self.ctr, pat1, [self.white], self.nsparks)

ctr = setup_control()
Crystal(ctr).launch_movie()
