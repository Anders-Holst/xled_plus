"""
Day 19 - Rotating Star

A rotating star on a color shifting background (and another star
behind it rotating the other way).
"""

from xled_plus.samples.sample_setup import *

class RotatingStarScene(Scene):
    def __init__(self, ctr):
        super(RotatingStarScene, self).__init__(ctr)
        self.star1c = Star(5, (0, 0), 0.0, 0.25, 0.1, hsl_color(0.38, 1.0, 0.4))
        self.star1b = Star(5, (0, 0), 0.0, 0.5, 0.2, hsl_color(0.40, 1.0, 0.2))
        self.star1a = Star(5, (0, 0), 0.0, 0.75, 0.3, hsl_color(0.42, 1.0, 0.0))
        self.star2 = Star(5, (0, 0), 0.0, 0.75, 0.4, hsl_color(0.48, 1.0, 0.1))
        self.star1a.set_torque(24 / self.preferred_fps)
        self.star1b.set_torque(24 / self.preferred_fps)
        self.star1c.set_torque(24 / self.preferred_fps)
        self.star2.set_torque(-24 / self.preferred_fps)
        self.star1a.set_depth(1.2)
        self.star1b.set_depth(1.1)
        self.star1c.set_depth(1.0)
        self.star2.set_depth(2)
        self.add_shape(self.star1a)
        self.add_shape(self.star1b)
        self.add_shape(self.star1c)
        self.add_shape(self.star2)

    def update(self, step):
        self.star1a.update(step)
        self.star1b.update(step)
        self.star1c.update(step)
        self.star2.update(step)

    def reset(self, numframes):
        super(RotatingStarScene, self).reset(numframes)
        self.time = 0

    def getnext(self):
        pat1 = super(RotatingStarScene, self).getnext()
        hue = (0.875 + 0.5 * abs(0.5 - (float(self.time) / self.preferred_frames))) % 1.0
        patbg = ctr.make_layout_pattern(lambda pos: hsl_color(hue, 1.0, max(0.0, 0.9 - (pos[0]**2+pos[1]**2))), style="centered")
        vec = self.getoccupancy()
        pat = [pat1[i] if vec[i] else patbg[i] for i in range(self.ctr.num_leds)]
        self.time += 1
        return pat

ctr = setup_control()
ctr.adjust_layout_aspect(1.0)  # How many times wider than high is the led installation?
RotatingStarScene(ctr).launch_movie()
