"""
Day 16 - Wheel of whites

In my oppinion, the "Sunset" effect on the app is quite ugly and distasteful
with its saturated colors. It is not easy to save it. Nevertheless, to show
that this type of rotating pattern can be generated with xled_plus too, I
created this effect of tinted whites, or very light watercolors that could
well each have passed for white if they were not next to each other, slowly
rotating around a neutral white center.
"""

from xled_plus.samples.sample_setup import *

class WheelEffect(Effect):
    def __init__(self, ctr, cols, folds, speed):
        super(WheelEffect, self).__init__(ctr)
        self.cols = cols
        self.folds = folds
        self.ncols = len(cols) * folds
        self.speedfactor = float(speed) / self.preferred_fps
        self.preferred_frames = int(len(cols) * self.preferred_fps / speed)
        self.white = hsl_color(0.0, 0.0, 1.0)
    def getcolor(self, pos):
        a = m.atan2(pos[1], pos[0])
        r = m.sqrt(pos[0]**2 + pos[1]**2)
        n = round(a * self.ncols / (2 * m.pi) + self.tm * self.speedfactor)
        col = self.cols[int(n) % len(self.cols)]
        if r < 0.3:
            return self.white
        else:
            return col
    def reset(self, numframes):
        self.tm = 0
    def getnext(self):
        pat = self.ctr.make_layout_pattern(self.getcolor, "centered")
        self.tm += 1
        return pat

ctr = setup_control()
cols = [hsl_color(0.3995, 1.0000, 0.6110), hsl_color(0.6609, 1.0000, 0.7104), hsl_color(0.1321, 1.0000, 0.6374), hsl_color(0.4466, 1.0000, 0.5911), hsl_color(0.0395, 1.0000, 0.5389)]
WheelEffect(ctr, cols, 1, 0.3).launch_movie()
