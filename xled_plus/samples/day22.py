"""
Day 22 - Snowflakes

Falling snowflakes against a purple-blue background.
Mimics the snowfall effect you can download with the app. 
"""

from xled_plus.samples.sample_setup import *

x = 0.75 ** 0.5

snowflake1 = [
    ([0.0, -1.0], [0.0, 1.0], 0.0),
    ([-x, -0.5], [x, 0.5], 0.0),
    ([-x, 0.5], [x, -0.5], 0.0),
    ([0.0, -0.7], [-0.3*x, -0.85], 0.0),
    ([0.0, -0.7], [0.3*x, -0.85], 0.0),
    ([0.0, 0.7], [-0.3*x, 0.85], 0.0),
    ([0.0, 0.7], [0.3*x, 0.85], 0.0),
    ([-0.7*x, -0.35], [-0.7*x, -0.65], 0.0),
    ([-0.7*x, 0.35], [-0.7*x, 0.65], 0.0),
    ([0.7*x, -0.35], [0.7*x, -0.65], 0.0),
    ([0.7*x, 0.35], [0.7*x, 0.65], 0.0),
    ([-0.7*x, -0.35], [-x, -0.2], 0.0),
    ([-0.7*x, 0.35], [-x, 0.2], 0.0),
    ([0.7*x, -0.35], [x, -0.2], 0.0),
    ([0.7*x, 0.35], [x, 0.2], 0.0),
]

snowflake2 = [
    ([0.0, -1.0], [0.0, 1.0], 0.0),
    ([-x, -0.5], [x, 0.5], 0.0),
    ([-x, 0.5], [x, -0.5], 0.0),
    ([0.0, -0.5], [-0.5*x, -0.25], 0.0),
    ([0.0, -0.5], [0.5*x, -0.25], 0.0),
    ([0.0, 0.5], [-0.5*x, 0.25], 0.0),
    ([0.0, 0.5], [0.5*x, 0.25], 0.0),
    ([0.5*x, 0.25], [0.5*x, -0.25], 0.0),
    ([-0.5*x, 0.25], [-0.5*x, -0.25], 0.0),
]

snowflake3 = [
    ([0.0, -0.5], [0.0, 0.5], 0.0),
    ([-0.5*x, -0.25], [0.5*x, 0.25], 0.0),
    ([-0.5*x, 0.25], [0.5*x, -0.25], 0.0),
]

snowflake4 = [
    ([0.0, -0.3], [-0.3*x, -0.15], 0.0),
    ([0.0, -0.3], [0.3*x, -0.15], 0.0),
    ([0.0, 0.3], [-0.3*x, 0.15], 0.0),
    ([0.0, 0.3], [0.3*x, 0.15], 0.0),
    ([0.3*x, 0.15], [0.3*x, -0.15], 0.0),
    ([-0.3*x, 0.15], [-0.3*x, -0.15], 0.0),
]

class Snowflake(Lineart2D):
    def __init__(self, segs, pos, angle, size, color):
        super(Snowflake, self).__init__()
        for seg in segs:
            self.add_segment(*seg)
        self.color = color
        self.size = size
        self.off = [0.0, 0.0]
        self.angle = 0.0
        self.speed = (0.0, 0.0)
        self.torque = 0.0
        self.change_pos(pos)
        self.change_angle(angle)

    def change_angle(self, deltaangle):
        self.angle += deltaangle
        ca = m.cos(self.angle * m.pi / 180.0) / self.size
        sa = m.sin(self.angle * m.pi / 180.0) / self.size
        self.mat = [[ca, sa], [-sa, ca]]

    def change_pos(self, delta):
        self.off = [self.off[0] - delta[0], self.off[1] - delta[1]]

    def update(self, step):
        self.change_pos((step * self.speed[0], step * self.speed[1]))
        self.change_angle(step * self.torque)

class SnowingScene(MovingShapesScene):
    def __init__(self, ctr):
        super(SnowingScene, self).__init__(ctr)
        self.freq = 0.6
        self.shapetypes = [snowflake1, snowflake2, snowflake3, snowflake4]
        self.shapeprobs = [0.15, 0.15, 0.3, 0.4]
        cf1 = random_hsl_color_func(hue=[0.06,0.12], sat=1.0, light=[0.2,0.6])
        cf2 = random_hsl_color_func(hue=[0.96,0.06], sat=0.7, light=0.0)
        self.shapecolfuncs = [cf1, cf1, cf2, cf2]
        self.horizon = 320
        self.preferred_frames = 640
        self.proj2D3D = "cylshell"

    def create(self):
        tp = randomdiscrete(self.shapeprobs)
        col = self.shapecolfuncs[tp]()
        dist = 2.0 + random() + (tp // 2)*2
        speed = 0.05 / dist
        rot = (random() - 0.5) * 6.0
        offset = (random() * 2 - 1.0, 1.5)
        vec = (0.0, -speed)
        sf = Snowflake(self.shapetypes[tp], offset, 0.0, 0.3, col)
        sf.speed = vec
        sf.torque = rot
        sf.set_depth(dist)
        sf.lw = 0.15
        sf.duetime = self.time + int(3.0 / speed)
        return sf

    def getnext(self):
        pat1 = super(SnowingScene, self).getnext()
        hue = (0.78 + 0.44 * abs(0.5 - (float(self.time) / 160) % 1.0)) % 1.0
        patbg = ctr.make_layout_pattern(lambda pos: hsl_color(hue, 1.0, -0.92), style="centered")
        vec = self.getoccupancy()
        pat = [pat1[i] if vec[i] else patbg[i] for i in range(self.ctr.num_leds)]
        return pat

ctr = setup_control()
ctr.adjust_layout_aspect(1.0)  # How many times wider than high is the led installation?
SnowingScene(ctr).launch_movie()
