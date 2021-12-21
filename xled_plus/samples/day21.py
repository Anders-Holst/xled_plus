"""
Day 21 - Moon

It is winter solstice - the longest night of the year.
And just a couple of days ago was a full moon.
This effect focuses on the night and the phases of the moon.
In it, the moon passes all of its phases in just a minute,
on a background of sparkling stars.

Again, gives best effect on a fairly dense 2D layout, and adjust
the aspect ratio below if you need.
"""

from xled_plus.samples.sample_setup import *

class Moon(Ellipse):
    def __init__(self, cent, rad, light, dark):
        super(Moon, self).__init__(cent, 0.0, rad, rad, None)
        self.light = light
        self.dark = dark
        self.r2 = rad*rad
        self.tilt = 0.5
        self.phase = -180.0
        self.speed = 1.0

    def moonlit(self, pos):
        ca = m.cos(m.pi * self.phase * self.tilt / 360.0)
        sa = m.sin(m.pi * self.phase * self.tilt / 360.0)
        cb = abs(m.cos(m.pi * (self.phase % 180.0) / 180.0))
        y = -ca * pos[1] + sa * pos[0]
        x = (-ca * pos[0] - sa * pos[1]) / cb if cb != 0.0 else 0.0
        if self.phase < -90:
            return x < 0.0 and x**2 + y**2 > self.r2
        elif self.phase == -90:
            return x < 0.0
        elif self.phase < 0:
            return x < 0.0 or x**2 + y**2 < self.r2
        elif self.phase < 90:
            return x > 0.0 or x**2 + y**2 < self.r2
        elif self.phase == 90:
            return x > 0.0
        else:
            return x > 0.0 and x**2 + y**2 > self.r2
        
    def update(self, step):
        self.phase = (self.phase + 180.0 + self.speed * step) % 360 - 180.0

    def get_color(self, coord):
        if self.is_inside(coord):
            if self.moonlit(coord):
                return self.light
            else:
                return self.dark
        else:
            return False

class MoonScene(MovingShapesScene):
    def __init__(self, ctr):
        super(MoonScene, self).__init__(ctr)
        self.bgeff = SparkleEffect(ctr, 3, self.whitefunc, pulselight_func(10, 1, 10))
        self.moon = Moon((0, 0), 0.4, hsl_color(0, 0, 1), (1, 1, 1))
        self.add_shape(self.moon)
        self.preferred_frames = 360
        self.preferred_fps = 6

    def whitefunc(self, *args):
        r = random()
        return hsl_color(0.05 if r < 0.5 else 0.45, 1.0, 0.8 - abs(r - 0.5))

    def update(self, step):
        self.moon.update(step)
        
    def reset(self, numframes):
        self.bgeff.reset(numframes)

    def getnext(self):
        pat1 = super(MoonScene, self).getnext()
        pat2 = self.bgeff.getnext()
        vec = self.getoccupancy()
        pat = [pat1[i] if vec[i] else pat2[i] for i in range(self.ctr.num_leds)]
        return pat

ctr = setup_control()
ctr.adjust_layout_aspect(1.0)  # How many times wider than high is the led installation?
MoonScene(ctr).launch_movie()
