"""
Day 27 - Infinite Kaleidoscope

Slowly changing symmetric pattern of random colors, this time in never
ending new constellations. Also, the shapes have sharp borders, and
their colors follow a slowly changing color theme.
Again, looks best on a 2D layout, and with correctly adjusted aspect:
Change the number in the call to adjust_layout_aspect in the next to
last line of the code below.
"""

from xled_plus.samples.sample_setup import *

class MeanderingKaleidoScene(MovingShapesScene):
    def __init__(self, ctr, sym):
        super(MeanderingKaleidoScene, self).__init__(ctr)
        self.freq = 0.6
        self.symang = m.pi / sym
        self.cm1 = ColorMeander(start=(random(), 0.6, 0.0))
        self.cm2 = ColorMeander(start=(random(), 0.6, 0.0))
        self.bgcol = hsl_color(0, 0, -0.5)
        self.horizon = 320
        self.preferred_frames = 640
        self.proj2D3D = "halfsphere"

    def create(self):
        colrnd = random()
        if colrnd < 0.3:
            (h, s, l) = self.cm2.get_hsl()
            col = hsl_color(h % 1.0, s, l)
        elif colrnd < 0.7:
            (h, s, l) = self.cm1.get_hsl()
            col = hsl_color((h + colrnd - 0.5) % 1.0, s, l)
        else:
            (h, s, l) = self.cm1.get_hsl()
            col = hsl_color(h % 1.0, colrnd, l)
        speed = m.exp((random() - 0.5) * 1.1) / self.preferred_fps * 0.08
        rad = 0.1 + random() * 0.5
        angle = random() * 2 * m.pi
        offset = random() - 0.5
        vec = (m.sin(angle), m.cos(angle))
        cent = (-vec[0] * 1.5 + vec[1] * offset, -vec[1] * 1.5 - vec[0] * offset + 0.5)
        vel = (vec[0] * speed, vec[1] * speed)
        nstep = int(3.0 / speed)
        corners = int(random() * 4) + 3
        shape = Star(corners, cent, 0.0, rad, rad/2.0, col)
        shape.set_depth(rad)
        shape.set_speed(vel[0], vel[1])
        shape.duetime = self.time + nstep
        return shape

    def update(self, step):
        self.cm1.step()
        self.cm2.step()
        super(MeanderingKaleidoScene, self).update(step)

    def get_color(self, coord, ind):
        r = m.sqrt(coord[0] ** 2 + coord[1] ** 2)
        a = m.atan2(coord[1], coord[0])
        a = abs((a % (2 * self.symang)) - self.symang)
        return super(MeanderingKaleidoScene, self).get_color((m.sin(a) * r, m.cos(a) * r), ind)

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

ctr = setup_control()
ctr.adjust_layout_aspect(1.0)  # How many times wider than high is the led installation?
eff = MeanderingKaleidoScene(ctr, 6)
oldmode = ctr.get_mode()["mode"]
eff.launch_rt()
print("Started continuous effect - press Return to stop it")
input()
eff.stop_rt()
ctr.set_mode(oldmode)

