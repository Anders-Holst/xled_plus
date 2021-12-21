"""
Day 20 - Kaleidoscope

Slowly changing symmetric pattern of random colors.
Again, looks best on a 2D layout, and with correctly adjusted aspect:
Change the number in the call to adjust_layout_aspect in the next to
last line of the code below.
"""

from xled_plus.samples.sample_setup import *

class SoftKaleidoScene(MovingShapesScene):
    def __init__(self, ctr, sym, colfunc):
        super(SoftKaleidoScene, self).__init__(ctr)
        self.freq = 0.6
        self.symang = m.pi / sym
        self.colfunc = colfunc
        self.bgcol = hsl_color(0, 0, -0.5)
        self.horizon = 320
        self.preferred_frames = 640

    def create(self):
        col = self.colfunc(self.time)
        speed = m.exp((random() - 0.5) * 1.1) / self.preferred_fps * 0.08
        rad = 0.1 + random() * 0.3
        angle = random() * 2 * m.pi
        offset = random() - 0.5
        vec = (m.sin(angle), m.cos(angle))
        cent = (-vec[0] * 1.5 + vec[1] * offset, -vec[1] * 1.5 - vec[0] * offset + 0.5)
        vel = (vec[0] * speed, vec[1] * speed)
        nstep = int(3.0 / speed)
        shape = Blob(cent, rad, col)
        #shape = Ellipse(cent, 0.0, rad, rad, col)
        shape.set_depth(0.0)
        shape.set_speed(vel[0], vel[1])
        shape.duetime = self.time + nstep
        return shape

    def get_color(self, coord, ind):
        r = m.sqrt(coord[0] ** 2 + coord[1] ** 2)
        a = m.atan2(coord[1], coord[0])
        a = abs((a % (2 * self.symang)) - self.symang)
        return super(SoftKaleidoScene, self).get_color((m.sin(a) * r, m.cos(a) * r), ind)

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
        sumcol = tuple(map(lambda *args: int(round(sum(args) * maxbr / sumbr)), *cols))
        return sumcol

ctr = setup_control()
ctr.adjust_layout_aspect(1.0)  # How many times wider than high is the led installation?
SoftKaleidoScene(ctr, 5, random_hsl_color_func(light=0.0)).launch_movie()
