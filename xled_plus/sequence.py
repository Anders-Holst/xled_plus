"""
xled_plus.sequence
~~~~~~~~~~~~~~~~~~

Author: Anders Holst (anders.holst@ri.se), 2021

This module contains some classes for creating spatio-temporal cyclic color
sequences. That is, bands or gradients of colors moving across the leds in
some direction at some speed.

It assumes that a 2D or 3D layout is set on the leds, and that any adjustment
to the aspect ratio has been made with HighControlInterface.adjust_layout_aspect
to make the angles come out right. In the 2D case the 'angle' parameter below
is just a single angle, in degreed counted clockwise from the top. In the 3D
case, 'angle' is a tuple (theta, phi), where theta is the polar angle, and phi
the azimuthal angle.
"""


from xled_plus.effect_base import Effect
from xled_plus.colormeander import ColorMeander
from xled_plus.pattern import blendcolors, dimcolor
from xled_plus.ledcolor import hsl_color
import math as m


class Sequence(Effect):
    def __init__(self, ctr, seqfunc, speed, folds, angle=False):
        super(Sequence, self).__init__(ctr)
        self.seqfunc = seqfunc
        if not ctr.layout_bounds:
            ctr.fetch_layout()
        self.dim = ctr.layout_bounds["dim"]
        if self.dim > 1:
            theta = (
                (angle[0] if isinstance(angle, tuple) else angle or 0.0) * m.pi / 180.0
            )
            phi = (angle[1] if isinstance(angle, tuple) else 0.0) * m.pi / 180.0
            dy = m.cos(theta) * folds / 2.0
            dxz = m.sin(theta) * folds / 2.0
            if self.dim == 3:
                self.vect = (dxz * m.cos(phi), dy, dxz * m.sin(phi))
            else:
                self.vect = (dxz, dy)
        else:
            self.vect = (folds / 2.0,)
        self.speed = speed
        self.currpos = 0.0
        self.init_fps(self.preferred_fps)

    def init_fps(self, fps):
        self.preferred_fps = fps
        if self.speed % fps == 0:
            self.preferred_frames = 1
        else:
            cyclen = 1.0 / abs((self.speed / fps + 0.5) % 1.0 - 0.5)
            self.preferred_frames = int(round(cyclen))

    def set_vector(self, vec):
        assert len(vec) == self.dim
        self.vect = vec

    def dot(self, v1, v2):
        return sum(map(lambda x1, x2: x1 * x2, v1, v2))

    def reset(self, numframes):
        self.currpos = 0.0

    def update(self, step):
        self.currpos += self.speed * step

    def getnext(self):
        self.update(1.0 / self.preferred_fps)
        return self.ctr.make_layout_pattern(
            lambda pos: self.seqfunc((self.dot(self.vect, pos) + self.currpos) % 1.0),
            style="centered",
        )


class ColorSequence(Sequence):
    def __init__(self, ctr, cols, lens=False, speed=1.0, folds=1.0, angle=False):
        super(ColorSequence, self).__init__(ctr, self.getcolor, speed, folds, angle)
        if lens is False:
            self.lims = [(i + 1) / len(cols) for i in range(len(cols))]
        else:
            self.lims = []
            acc = 0.0
            tot = float(sum(lens))
            for i in range(len(cols)):
                acc += lens[i] / tot
                self.lims.append(acc)
        self.cols = [c for c in cols]

    def lookup(self, x, lims):
        for i in range(len(lims)):
            if x < lims[i]:
                return i
        return False

    def getcolor(self, x):
        return self.cols[self.lookup(x, self.lims)]


class GradientSequence(Sequence):
    def __init__(self, ctr, cols, lens=False, speed=1.0, folds=1.0, angle=0):
        super(GradientSequence, self).__init__(ctr, self.getcolor, speed, folds, angle)
        if lens is False:
            self.lims = [float(i) / len(cols) for i in range(len(cols) + 1)]
        else:
            self.lims = [0.0]
            acc = 0.0
            tot = float(sum(lens))
            for i in range(len(cols)):
                acc += lens[i] / tot
                self.lims.append(acc)
        self.lens = lens
        self.cols = [c for c in cols]
        self.cols.append(cols[0])

    def lookup(self, x, lims):
        for i in range(len(lims)):
            if x < lims[i]:
                return i
        return False

    def getcolor(self, x):
        ind = self.lookup(x, self.lims)
        return blendcolors(
            self.cols[ind - 1],
            self.cols[ind],
            (x - self.lims[ind - 1]) / (self.lims[ind] - self.lims[ind - 1]),
        )


class SpectrumSequence(Sequence):
    def __init__(self, ctr, lightness=0.0, angle=False):
        super(SpectrumSequence, self).__init__(ctr, self.getcolor, 0.2, 1.0, angle)
        self.lightness = lightness

    def getcolor(self, x):
        return hsl_color(x, 1.0, self.lightness)


class RotatingAngleSequence(Sequence):
    def initialize(self, torque):
        deltaang = m.pi / 180.0 * torque / self.preferred_fps
        self.sa = m.sin(deltaang)
        self.ca = m.cos(deltaang)
        if self.dim == 1:
            self.ivect = (self.vect[0], 0.0)

    def update(self, step):
        if self.dim == 3:
            self.vect = (
                self.vect[0] * self.ca + self.vect[2] * self.sa,
                self.vect[1],
                self.vect[2] * self.ca - self.vect[0] * self.sa,
            )
        elif self.dim == 2:
            self.vect = (
                self.vect[0] * self.ca + self.vect[1] * self.sa,
                self.vect[1] * self.ca - self.vect[0] * self.sa,
            )
        else:
            self.ivect = (
                self.ivect[0] * self.ca + self.ivect[1] * self.sa,
                self.ivect[1] * self.ca - self.ivect[0] * self.sa,
            )
            self.vect = (self.ivect[0], )
        self.currpos += self.speed * step


class RotatingAngleColorSequence(ColorSequence, RotatingAngleSequence):
    def __init__(self, ctr, cols, lens=False, speed=1.0, folds=1.0, angle=False, torque=False):
        super(RotatingAngleColorSequence, self).__init__(ctr, cols, speed=speed, folds=folds, angle=angle)
        self.initialize(torque)


class RotatingAngleGradientSequence(GradientSequence, RotatingAngleSequence):
    def __init__(self, ctr, cols, lens=False, speed=1.0, folds=1.0, angle=False, torque=False):
        super(RotatingAngleGradientSequence, self).__init__(ctr, cols, speed=speed, folds=folds, angle=angle)
        self.initialize(torque)


class VaryingAngleSequence(Sequence):
    def initialize(self, maxfold):
        self.maxfold = maxfold
        if self.dim == 3:
            self.mangle = ColorMeander("sphere")
        else:
            self.mangle = ColorMeander("cylinder")

    def update(self, step):
        self.mangle.step()
        (x, y, z) = self.mangle.get_xyz()
        if self.dim == 3:
            self.vect = (
                x * self.maxfold / 2.0,
                y * self.maxfold / 2.0,
                z * self.maxfold / 2.0,
            )
        elif self.dim == 2:
            self.vect = (x * self.maxfold / 2.0, y * self.maxfold / 2.0)
        else:
            self.vect = (z * self.maxfold / 2.0,)
        self.currpos += self.speed * step


class VaryingAngleColorSequence(ColorSequence, VaryingAngleSequence):
    def __init__(self, ctr, cols, lens=False, speed=1.0, folds=3.0):
        super(VaryingAngleColorSequence, self).__init__(ctr, cols, speed, folds)
        self.initialize(folds)


class VaryingAngleGradientSequence(GradientSequence, VaryingAngleSequence):
    def __init__(self, ctr, cols, lens=False, speed=1.0, folds=3.0):
        super(VaryingAngleGradientSequence, self).__init__(ctr, cols, speed, folds)
        self.initialize(folds)


class MeanderingSequence(VaryingAngleSequence):
    def __init__(self, ctr, fixangle=False):
        super(MeanderingSequence, self).__init__(ctr, self.getcolor, 0.0, 1.0, fixangle)
        self.fixangle = fixangle
        self.initialize(1.0)
        self.cm = ColorMeander("sphere")
        self.colvec = [self.cm.get()] * 200
        self.iter = 1
        self.init_fps(2)
        self.preferred_frames = 800

    def reset(self, numframes):
        self.currpos = 0.5
        if numframes:
            self.mangle.steplen *= 10
            self.mangle.noiselev *= 3
            self.iter = 9
            self.preferred_fps /= 10

    def update(self, step):
        if self.fixangle is False:
            super(MeanderingSequence, self).update(step)
        for i in range(self.iter):
            self.cm.step()
            self.colvec = [self.cm.get()] + self.colvec[:-1]

    def getcolor(self, x):
        ind = int(x * len(self.colvec) - 0.5)
        return self.colvec[min(max(0, ind), len(self.colvec)-1)]


class MeanderingTandemSequence(VaryingAngleSequence):
    def __init__(self, ctr, gap=False, fixangle=False):
        super(MeanderingTandemSequence, self).__init__(ctr, self.getcolor, 0.0, 1.0, fixangle)
        self.initialize(1.0)
        self.gap = gap
        self.fixangle = fixangle
        self.cm = ColorMeander("sphere")
        self.init_fps(2)
        self.preferred_frames = 800

    def reset(self, numframes):
        self.currpos = 0.5
        if numframes:
            self.cm.steplen *= 10
            self.cm.noiselev *= 3
            self.preferred_fps /= 10

    def update(self, step):
        if self.fixangle is False:
            super(MeanderingTandemSequence, self).update(step)
        self.cm.step()
        (h, s, l) = self.cm.get_hsl()
        self.hsl1 = (h, s, l)
        self.hsl2 = ((h + 0.5) % 1.0, s, l)

    def getcolor(self, x):
        hsl = self.hsl1 if x < 0.5 else self.hsl2
        fact = min(1.0, abs(2*x - 1.0) / abs(self.gap)) if self.gap else 1.0
        if self.gap >= 0.0:
            return hsl_color(hsl[0], hsl[1]*fact, hsl[2])
        else:
            return hsl_color(hsl[0], hsl[1], hsl[2]) if fact == 1.0 else (0,0,0)

