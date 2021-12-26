"""
Day 24 - Christmas Tree Balls

Colored balls moving against a glittering white background.
Merry Christmas!
"""

from xled_plus.samples.sample_setup import *

class ChristmasBallsScene(MovingShapesScene):
    def __init__(self, ctr, cols):
        super(ChristmasBallsScene, self).__init__(ctr)
        self.freq = 0.5
        self.colors = cols
        self.whites = [hsl_color(0.4, 0.5, 0.2), hsl_color(0.1, 0.5, 0.2), hsl_color(0.0, 0.0, 0.2)]
        self.blink = hsl_color(0.0, 0.0, 1.0)
        self.bgpat = make_random_select_color_pattern(ctr, self.whites)
        self.preferred_frames = 640
        self.proj2D3D = "cylshell"

    def create(self):
        tp = int(random() * len(self.colors))
        speed = 0.02
        angle = random() * 2 * m.pi
        offset = (random() - 0.5) * 1.6
        vec = (m.sin(angle), m.cos(angle))
        cent = (-vec[0] * 1.5 + vec[1] * offset, -vec[1] * 1.5 - vec[0] * offset)
        vel = (vec[0] * speed, vec[1] * speed)
        nstep = int(3.0 / speed)
        sh = Ellipse(cent, 0.0, 0.16, 0.16, self.colors[tp])
        sh.set_speed(vel[0], vel[1])
        sh.set_depth(0.0)
        sh.duetime = self.time + nstep
        return sh
        
    def getnext(self):
        pat1 = super(ChristmasBallsScene, self).getnext()
        patbg = sprinkle_pattern(self.ctr, self.bgpat, [self.blink], 0.05*self.ctr.num_leds)
        vec = self.getoccupancy()
        pat = [pat1[i] if vec[i] else patbg[i] for i in range(self.ctr.num_leds)]
        return pat

ctr = setup_control()
ctr.adjust_layout_aspect(1.0)  # How many times wider than high is the led installation?
cols = [hsl_color(0.625, 1.0, -0.15), hsl_color(0.26, 1.0, -0.11), hsl_color(0.42, 1.0, -0.05), hsl_color(0.54, 1.0, -0.15)]
# cols = [hsl_color(0.44, 1.0, -0.21), hsl_color(0.44, 1.0, 0.11), hsl_color(0.625, 1.0, -0.17), hsl_color(0.625, 1.0, 0.11)]
ChristmasBallsScene(ctr, cols).launch_movie()
