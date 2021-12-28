"""
Day 28 - Flowers

Different colored flowers that bloom from the center. 
Similar principle as the Kaleidoscope, but grow pieces from the center.
Again, looks best on a 2D layout, and with correctly adjusted aspect:
Change the number in the call to adjust_layout_aspect in the code below.
"""

from xled_plus.samples.sample_setup import *

class FlowerScene(MovingShapesScene):
    def __init__(self, ctr, sym):
        super(FlowerScene, self).__init__(ctr)
        self.freq = 0.6
        self.symang = m.pi / sym
        self.bgcol = hsl_color(0.25, 1.0, -0.5)
        self.lasthue = 0.25
        self.horizon = 360
        self.preferred_frames = 720
        self.proj2D3D = "halfsphere"
        self.ind = 0

    def makecolorfunc(self, sh):
        hue = (random()*0.74 + 0.36) % 1.0
        while abs(hue - self.lasthue) < 0.1:
            hue = (random()*0.74 + 0.36) % 1.0
        self.lasthue = hue
        sat = random()*0.5 + 0.5
        aa = 0.2
        ss = 0.05 / self.preferred_fps
        def func(pos, ind):
            tm = self.time - sh.crtime
            if tm * ss < aa:
                return hsl_color(hue, sat, 0.0)
            else:
                delta = 2.0 - 2.0 * aa / (tm * ss)
                rad = (pos[0]**2 + pos[1]**2) ** 0.5
                satres = rad * delta / (tm * ss) + 1.0 - delta
                return hsl_color(hue, max(0.0, min(1.0, sat * satres)), 0.0)
        return func

    def reshapefunc(self, sh):
        fact = (random() - 0.4) * 0.7
        aa = 0.2
        ss = 0.05 / self.preferred_fps
        def func():
            tm = self.time - sh.crtime
            if tm * ss < aa:
                sh.cent = (0.0, 0.0)
                sh.rad1 = tm * ss
                sh.rad2 = sh.rad1
            else:
                st = tm - aa / ss
                sh.cent = (sh.speed[0] * ss * st * 0.5, sh.speed[1] * ss * st * 0.5)
                sh.rad2 = aa + st * ss * 0.5
                sh.rad1 = aa + st * fact * ss * 0.5
        return func

    def create(self):
        angle = (random() * 3.0 - 0.5) * self.symang
        vec = (m.sin(angle), m.cos(angle))
        shape = Ellipse((0.0, 0.0), angle, 0.0, 0.0, False)
        shape.crtime = self.time
        shape.color = self.makecolorfunc(shape)
        shape.reshape = self.reshapefunc(shape)
        shape.set_depth(-self.ind)
        shape.set_speed(vec[0], vec[1])
        self.ind += 1
        return shape

    def update(self, step):
        if self.time % 30 == 0:
            if self.record:
                sh = self.create()
                self.add_shape(sh)
                self.pre_shapes.append((self.time + self.preferred_frames, sh))
            elif self.pre_shapes and self.pre_shapes[0][0] <= self.time:
                sh = self.pre_shapes[0][1]
                sh.crtime = self.time
                sh.set_depth(-self.ind)
                self.ind += 1
                self.add_shape(sh)
                self.pre_shapes = self.pre_shapes[1:]
            else:
                self.add_shape(self.create())
        for sh in self.shapes:
            sh.reshape()
        if len(self.shapes) > 12:
            self.shapes = self.shapes[:-1]
        self.time += 1
        # super(FlowerScene, self).update(step)

    def get_color(self, coord, ind):
        r = m.sqrt(coord[0] ** 2 + coord[1] ** 2)
        a = m.atan2(coord[1], coord[0])
        a = abs((a % (2 * self.symang)) - self.symang)
        return super(FlowerScene, self).get_color((m.sin(a) * r, m.cos(a) * r), ind)

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

if __name__ == '__main__':
    ctr = setup_control()
    ctr.adjust_layout_aspect(1.4)  # How many times wider than high is the led installation?
    eff = FlowerScene(ctr, 6)
    oldmode = ctr.get_mode()["mode"]
    eff.launch_rt()
    print("Started continuous effect - press Return to stop it")
    input()
    eff.stop_rt()
    ctr.set_mode(oldmode)

