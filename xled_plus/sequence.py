from xled.effect_base import Effect
from xled.colormeander import ColorMeander
from xled.pattern import blendcolors
from xled.ledcolor import hsl_color
import math as m

# Spatio-temporal cyclic color sequences


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


class VaryingAngleSequence(Sequence):
    def initialize(self, dim, maxfold):
        self.dim = dim
        self.maxfold = maxfold
        if dim == 3:
            self.meander = ColorMeander("sphere")
        else:
            self.meander = ColorMeander("cylinder")

    def update(self, step):
        self.meander.step()
        (x, y, z) = self.meander.get_xyz()
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


class InfiniteSequence(Sequence):
    def __init__(self):
        pass
