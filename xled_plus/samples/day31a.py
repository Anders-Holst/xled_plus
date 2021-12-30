"""
Day 31 - Fireworks (version A)

My take on the fireworks theme. Colored blobs growing and sparkling.
This version gives one explosion at a time at controlled intervalls.
Suits best for smaller nonregular installations, eg a christmas tree.
Also check the version in day31b.
"""

from xled_plus.samples.sample_setup import *


class Fireball(Shape):
    def __init__(self, cent, minrad, maxrad, speed, huesat):
        super(Fireball, self).__init__(cent, 0.0)
        self.rad = minrad
        self.minrad = minrad
        self.maxrad = maxrad
        self.speed = speed
        self.huesat = huesat

    def is_inside(self, coord):
        return (
            sum(map(lambda x1, x2: (x1 - x2) ** 2, self.cent, coord)) <= self.rad ** 2
        )

    def get_color(self, coord, ind):
        dist2 = (
            sum(map(lambda x1, x2: (x1 - x2) ** 2, self.cent, coord)) / self.rad ** 2
        )
        if dist2 > 1.0:
            return False
        elif self.rad == self.minrad:
            return hsl_color(0.0, 0.0, 1.0)
        else:
            (hue, sat) = self.huesat
            p = (self.rad - self.minrad) / (self.maxrad - self.minrad)
            rnd = random()
            if rnd < 0.1 * (1.2 - p):
                light = 1.0
            elif rnd < 0.2 * (1.2 - p):
                light = 0.0
            else:
                light = 2.0 * (1.0 - p) ** 2 - 1.0
            return hsl_color(hue, sat, light)

    def update(self, step):
        self.rad += self.speed * step


class FireworksScene(MovingShapesScene):
    def __init__(self, ctr):
        super(FireworksScene, self).__init__(ctr)
        self.freq = 0.0
        self.horizon = 100
        self.preferred_frames = 700
        self.preferred_fps = 20
        self.proj2D3D = "halfsphere"

    def create(self):
        cent = (0.0, 0.0)
        shape = Fireball(cent, 0.10, 1.0, 0.01, (random(), 1.0 - random()**2))
        shape.duetime = self.time + 0.9/0.01
        return shape

    def update(self, step):
        for sh in reversed(self.shapes):
            if sh.duetime < self.time:
                self.shapes.remove(sh)
        if self.time >= self.crtime:
            if self.record:
                sh = self.create()
                self.add_shape(copy(sh))
                sh.duetime += self.preferred_frames
                self.crtime = self.time + 100
                self.pre_shapes.append((self.crtime + self.preferred_frames, sh))
            elif self.replay:
                if self.pre_shapes:
                    self.add_shape(self.pre_shapes[0][1])
                    self.crtime = self.pre_shapes[0][0]
                    self.pre_shapes = self.pre_shapes[1:]
            else:
                self.add_shape(self.create())
                self.crtime = self.time + 100
                if self.pre_shapes and self.crtime >= self.pre_shapes[0][0]:
                    self.replay = True
        for sh in self.shapes:
            sh.update(step)
        self.time += step

if __name__ == '__main__':
    ctr = setup_control()
    ctr.adjust_layout_aspect(1.0)  # How many times wider than high is the led installation?
    eff = FireworksScene(ctr)
    oldmode = ctr.get_mode()["mode"]
    eff.launch_rt()
    print("Started continuous effect - press Return to stop it")
    input()
    eff.stop_rt()
    ctr.set_mode(oldmode)
