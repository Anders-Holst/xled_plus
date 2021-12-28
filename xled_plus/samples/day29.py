"""
Day 29 - Bouncing Balls

Balls of slowly changing colors, bouncing over the leds.
Unlike the previous effects, this should work reasonably for both 2D and 3D layouts.
Works best for fairly dense layouts though.
A continuous effect. You can upload it as a movie instead if you prefer, but it will jerk in the transition.
Remember to adjust aspect ratio in the call to adjust_layout_aspect in the code below.
"""

from xled_plus.samples.sample_setup import *

class MeanderBouncingScene(BouncingScene):
    def __init__(self, ctr, num, speed=0.25, size=0.3):
        super(MeanderBouncingScene, self).__init__(ctr, num, speed, size, False)
        self.bgcol = hsl_color(0.0, 0.0, -0.5)
        self.bgeffect = BreathEffect(ctr, [(0.0, 0.0, 0.0)], 1.0, 0.75, [12, 30])
        self.colfunc = False
        self.horizon = 0
        self.preferred_frames = 640

    def create(self):
        sh = super(MeanderBouncingScene, self).create()
        sh.cm = ColorMeander("surface", start=(random(), 1.0, 0.0))
        return sh

    def update(self, step):
        for sh in self.shapes:
            sh.cm.step()
            (h, s, l) = sh.cm.get_hsl()
            sh.color = hsl_color(h, 1.0, min(0.3, max(-0.3, l)))
        super(MeanderBouncingScene, self).update(step)

    def blend_colors(self, colors):
        cols = colors
        br = list(map(lambda rgb: color_brightness(*rgb), colors))
        maxbr = max(br) if br else 0.0
        sumbr = sum(br) if br else 0.0
        bgbr = color_brightness(*self.bgcol)
        if maxbr < bgbr:
            delta = (bgbr - maxbr) / bgbr
            sumbr += (bgbr - maxbr)
            maxbr = bgbr
            cols = cols + [tuple(map(lambda x: x*delta, self.bgcol))]
        sumcol = tuple(map(lambda *args: max(0, min(255, int(round(sum(args) * maxbr / sumbr)))), *cols))
        return sumcol

    def reset(self, numframes):
        super(MeanderBouncingScene, self).reset(numframes)
        self.bgeffect.reset(numframes)

    def getnext(self):
        pat1 = super(MeanderBouncingScene, self).getnext()
        patbg = self.bgeffect.getnext()
        vec = self.getoccupancy()
        pat = [pat1[i] if vec[i] else patbg[i] for i in range(self.ctr.num_leds)]
        return pat


if __name__ == '__main__':
    ctr = setup_control()
    ctr.adjust_layout_aspect(1.0)  # How many times wider than high is the led installation?
    eff = MeanderBouncingScene(ctr, 5, size=0.4)
    oldmode = ctr.get_mode()["mode"]
    eff.launch_rt()
    print("Started continuous effect - press Return to stop it")
    input()
    eff.stop_rt()
    ctr.set_mode(oldmode)
