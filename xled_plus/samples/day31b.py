"""
Day 31 - Fireworks (version B)

My take on the fireworks theme. Colored blobs growing and sparkling.
This version gives explosions at random times and positions.
Suits best for rather large and dense 2D installations.
Also check the version in day31a.
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
        self.freq = 0.8
        self.horizon = 60
        self.preferred_frames = 720
        self.preferred_fps = 20
        self.proj2D3D = "cylshell"

    def create(self):
        cent = (random()*1.6 - 0.8, random()*1.6 - 0.8)
        shape = Fireball(cent, 0.15, 0.63, 0.008, (random(), 1.0))
        shape.duetime = self.time + 0.48/0.008
        return shape


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
