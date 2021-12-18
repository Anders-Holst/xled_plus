"""
xled_plus.shapes
~~~~~~~~~~~~~~~~

Author: Anders Holst (anders.holst@ri.se), 2021

This module contains classes for creating scenes of moving (or still) objects.
Objects implemented are various geometrical shapes, such as polygons, stars,
and circles, but also simple letters and numbers. 
"""


import math as m
from random import random, gauss
from copy import copy

from xled_plus.ledcolor import hsl_color
from xled_plus.effect_base import Effect
from xled_plus.colormeander import ColorMeander
from xled_plus.pattern import random_hsl_color_func



class Scene(Effect):
    def __init__(self, ctr):
        super(Scene, self).__init__(ctr)
        self.shapes = []
        self.occvec = [False] * ctr.num_leds

    def add_shape(self, sh):
        self.shapes.append(sh)
        self.shapes.sort(key=lambda sh: sh.get_depth())

    def remove_shape(self, sh):
        self.shapes.remove(sh)

    def update(self, step):
        for sh in self.shapes:
            sh.update(step)

    def blend_colors(self, colors):
        if colors:
            return tuple(map(lambda *args: int(round(sum(args) / len(args))), *colors))
        else:
            return (0, 0, 0)

    def get_color(self, coord, ind):
        goaldepth = False
        colors = []
        for sh in self.shapes:
            if goaldepth and sh.get_depth != goaldepth:
                break
            else:
                col = sh.get_color(coord)
                if col:
                    if not goaldepth:
                        goaldepth = sh.get_depth()
                    colors.append(col)
        self.occvec[ind] = True if colors else False
        return self.blend_colors(colors)

    def reset(self, numframes):
        pass

    def getnext(self):
        self.update(1)
        return self.ctr.make_layout_pattern(self.get_color, style="centered", index=True)

    def getoccupancy(self):
        return self.occvec


class Shape(object):
    def __init__(self):
        self.depth = 0

    def is_inside(self, coord):
        pass

    def get_color(self, coord):
        pass

    def get_depth(self):
        return self.depth

    def set_depth(self, depth):
        self.depth = depth

    def update(self, step):
        pass


class MovingShape(Shape):
    def __init__(self, cent, angle):
        super(MovingShape, self).__init__()
        self.cent = cent
        self.angle = angle * m.pi / 180.0
        self.speed = (0.0, 0.0)
        self.torque = 0.0

    def set_speed(self, vx, vy):
        self.speed = (vx, vy)

    def set_torque(self, va):
        self.torque = va * m.pi / 180.0

    def update(self, step):
        self.cent = (
            self.cent[0] + step * self.speed[0],
            self.cent[1] + step * self.speed[1],
        )
        self.angle = (self.angle + step * self.torque) % 360.0


class Blob(MovingShape):
    def __init__(self, cent, rad, col):
        super(Blob, self).__init__(cent, 0.0)
        self.rad = rad
        self.color = col

    def is_inside(self, coord):
        return (
            sum(map(lambda x1, x2: (x1 - x2) ** 2, self.cent, coord)) <= self.rad ** 2
        )

    def get_color(self, coord):
        dist = (
            m.sqrt(sum(map(lambda x1, x2: (x1 - x2) ** 2, self.cent, coord))) / self.rad
        )
        if dist > 1.0:
            return False
        else:
            return tuple(map(lambda x: int(round(x * (1.0 - dist))), self.color))


class Polygon(MovingShape):
    def __init__(self, num, cent, angle, smallrad, col):
        assert num >= 3
        super(Polygon, self).__init__(cent, angle)
        self.num = num
        self.rad1 = smallrad
        self.rad2 = smallrad / m.cos(m.pi / num)
        self.color = col

    def is_inside(self, coord):
        dist = m.sqrt(sum(map(lambda x1, x2: (x1 - x2) ** 2, self.cent, coord)))
        if dist > self.rad2:
            return False
        elif dist <= self.rad1:
            return True
        else:
            dp = list(map(lambda x1, x2: (x1 - x2), self.cent, coord))
            ang = (self.angle + m.atan2(dp[0], -dp[1]) + m.pi / self.num) % (
                2 * m.pi / self.num
            ) - m.pi / self.num
            return dist <= self.rad1 / m.cos(ang)

    def get_color(self, coord):
        if self.is_inside(coord):
            return self.color
        else:
            return False


class Ellipse(MovingShape):
    def __init__(self, cent, angle, largerad, smallrad, col):
        super(Ellipse, self).__init__(cent, angle)
        self.rad1 = smallrad
        self.rad2 = largerad
        self.color = col

    def is_inside(self, coord):
        dist = m.sqrt(sum(map(lambda x1, x2: (x1 - x2) ** 2, self.cent, coord)))
        if dist > self.rad2:
            return False
        elif dist <= self.rad1:
            return True
        else:
            dp = list(map(lambda x1, x2: (x1 - x2), self.cent, coord))
            ang = -self.angle + m.atan2(dp[0], dp[1])
            return dist <= self.rad1 * self.rad2 / m.sqrt(
                (self.rad1 * m.cos(ang)) ** 2 + (self.rad2 * m.sin(ang)) ** 2
            )

    def get_color(self, coord):
        if self.is_inside(coord):
            return self.color
        else:
            return False


class Star(MovingShape):
    def __init__(self, num, cent, angle, largerad, smallrad, col):
        assert num >= 2
        super(Star, self).__init__(cent, angle)
        self.num = num
        self.set_radius(largerad, smallrad)
        self.color = col

    def set_radius(self, largerad, smallrad):
        self.rad1 = smallrad
        self.rad2 = largerad
        self.ang0 = m.atan(
            (m.cos(m.pi / self.num) - smallrad / largerad) / m.sin(m.pi / self.num)
        )
        self.rad0 = smallrad * m.cos(self.ang0)

    def is_inside(self, coord):
        dist = m.sqrt(sum(map(lambda x1, x2: (x1 - x2) ** 2, self.cent, coord)))
        if dist > self.rad2:
            return False
        elif dist <= self.rad1:
            return True
        else:
            dp = list(map(lambda x1, x2: (x1 - x2), self.cent, coord))
            ang = abs(
                (-self.angle + m.atan2(dp[0], dp[1])) % (2 * m.pi / self.num)
                - m.pi / self.num
            )
            return dist <= self.rad0 / m.cos(ang + self.ang0)

    def get_color(self, coord):
        if self.is_inside(coord):
            return self.color
        else:
            return False


# Tänk ett antal punkter med linjer eller arcs mellan
# Vidare en standardstorlek och linjevidd, som kan skalas och få en riktning
#
# En arc (p1, p2, ang). centrum (0,0) start (-1,0) vinkel ang -> slutpunkt (-cos(ang), sin(ang))
# Hitta en mappning p = A + Rx så att (-1,0) -> p1 och (-c,s) -> p2
#
# R*(x,y) = (0,x^2+y^2) -> ((y, -x),(x, y))
#
class Lineart2D(Shape):
    def __init__(self):
        self.points = []
        self.lines = []
        self.arcs = []
        self.extent = [0.0, 0.0, 0.0, 0.0]  # minx miny maxx maxy
        self.off = [0.0, 0.0]
        self.mat = [[1.0, 0.0], [0.0, 1.0]]
        self.lw = 0.1
        self.color = (0, 0, 0)

    def add_extent(self, minx, miny, maxx, maxy):
        if self.extent[0] > minx:
            self.extent[0] = minx
        if self.extent[1] > miny:
            self.extent[1] = miny
        if self.extent[2] < maxx:
            self.extent[2] = maxx
        if self.extent[3] < maxy:
            self.extent[3] = maxy

    def add_segment(self, p1, p2, ang):
        # If p1==p2 its a point, if ang==0 its a line, else its an arc
        # In all cases, produce a local transformation A + Rx, and increase extent
        if p1 == p2:
            self.points.append([-p1[0], -p1[1]])
            self.add_extent(p1[0], p1[1], p1[0], p1[1])
        elif ang == 0.0:
            dp = [p2[0] - p1[0], p2[1] - p1[1]]
            rad = m.sqrt(dp[0] * dp[0] + dp[1] * dp[1])
            self.lines.append(
                (
                    [-p1[0], -p1[1]],
                    [[dp[1] / rad, -dp[0] / rad], [dp[0] / rad, dp[1] / rad]],
                    rad,
                )
            )
            self.add_extent(
                min(p1[0], p2[0]),
                min(p1[1], p2[1]),
                max(p1[0], p2[0]),
                max(p1[1], p2[1]),
            )
            tmp = [-p1[0], -p1[1]]
            if tmp not in self.points:
                self.points.append(tmp)
            tmp = [-p2[0], -p2[1]]
            if tmp not in self.points:
                self.points.append(tmp)
        else:
            if ang < 0.0:
                ang = -ang
                (p1, p2) = (p2, p1)
            cot = m.tan((180.0 - ang) * m.pi / 360.0) / 2.0
            dp = [p2[0] - p1[0], p2[1] - p1[1]]
            cent = [dp[0] * 0.5 + dp[1] * cot, dp[1] * 0.5 - dp[0] * cot]
            rad = m.sqrt(cent[0] * cent[0] + cent[1] * cent[1])
            aa = ang * m.pi / 180.0 - m.pi
            self.arcs.append(
                (
                    [-p1[0] - cent[0], -p1[1] - cent[1]],
                    [[cent[0] / rad, cent[1] / rad], [-cent[1] / rad, cent[0] / rad]],
                    rad,
                    aa,
                )
            )
            self.add_extent(
                min(p1[0], p2[0])
                if m.atan2(-cent[1], -cent[0]) > aa
                else p1[0] + cent[0] - rad,
                min(p1[1], p2[1])
                if m.atan2(cent[0], -cent[1]) > aa
                else p1[1] + cent[1] - rad,
                max(p1[0], p2[0])
                if m.atan2(cent[1], cent[0]) > aa
                else p1[0] + cent[0] + rad,
                max(p1[1], p2[1])
                if m.atan2(-cent[0], cent[1]) > aa
                else p1[1] + cent[1] + rad,
            )
            tmp = [-p1[0], -p1[1]]
            if tmp not in self.points:
                self.points.append(tmp)
            tmp = [-p2[0], -p2[1]]
            if tmp not in self.points:
                self.points.append(tmp)

    def trans(self, coord, off, mat):
        return [
            (off[0] + coord[0]) * mat[0][0] + (off[1] + coord[1]) * mat[0][1],
            (off[0] + coord[0]) * mat[1][0] + (off[1] + coord[1]) * mat[1][1],
        ]

    def is_inside(self, coord):
        # global transform
        # jämför extent
        # för varje segment, lokal transform och kolla närhet
        pp = self.trans(coord, self.off, self.mat)
        if (
            pp[0] < self.extent[0] - self.lw * 0.5
            or pp[1] < self.extent[1] - self.lw * 0.5
            or pp[0] > self.extent[2] + self.lw * 0.5
            or pp[1] > self.extent[3] + self.lw * 0.5
        ):
            return False
        for seg in self.points:
            p0 = [pp[0] + seg[0], pp[1] + seg[1]]
            if p0[0] * p0[0] + p0[1] * p0[1] <= self.lw * self.lw / 4:
                return True
        for seg in self.lines:
            p0 = self.trans(pp, seg[0], seg[1])
            if (
                p0[0] <= self.lw / 2
                and p0[0] >= -self.lw / 2
                and p0[1] >= 0.0
                and p0[1] <= seg[2]
            ):
                return True
        for seg in self.arcs:
            p0 = self.trans(pp, seg[0], seg[1])
            r = m.sqrt(p0[0] * p0[0] + p0[1] * p0[1])
            a = m.atan2(-p0[1], p0[0])
            if r >= seg[2] - self.lw / 2 and r <= seg[2] + self.lw / 2 and a <= seg[3]:
                return True
        return False

    def get_color(self, coord):
        if self.is_inside(coord):
            return self.color
        else:
            return False


letters = {
    "A": [
        ([-0.35, 0.0], [-0.05, 1.0], 0.0),
        ([0.35, 0.0], [0.05, 1.0], 0.0),
        ([-0.05, 1.0], [0.05, 1.0], 0.0),
        ([-0.2, 0.5], [0.2, 0.5], 0.0),
    ],
    "B": [
        ([-0.35, 0.0], [-0.35, 1.0], 0.0),
        ([-0.35, 1.0], [0.1, 1.0], 0.0),
        ([-0.35, 0.5], [0.1, 0.5], 0.0),
        ([-0.35, 0.0], [0.1, 0.0], 0.0),
        ([0.1, 1.0], [0.1, 0.5], 180.0),
        ([0.1, 0.5], [0.1, 0.0], 180.0),
    ],
    "C": [
        ([-0.35, 0.35], [0.247, 0.103], -135.0),
        ([-0.35, 0.65], [0.247, 0.897], 135.0),
        ([-0.35, 0.35], [-0.35, 0.65], 0.0),
    ],
    "D": [
        ([-0.35, 0.0], [-0.35, 1.0], 0.0),
        ([-0.35, 1.0], [0.0, 1.0], 0.0),
        ([-0.35, 0.0], [0.0, 0.0], 0.0),
        ([0.0, 1.0], [0.35, 0.65], 90.0),
        ([0.0, 0.0], [0.35, 0.35], -90.0),
        ([0.35, 0.25], [0.35, 0.75], 0.0),
    ],
    "E": [
        ([-0.35, 0.0], [-0.35, 1.0], 0.0),
        ([-0.35, 1.0], [0.35, 1.0], 0.0),
        ([-0.35, 0.5], [0.25, 0.5], 0.0),
        ([-0.35, 0.0], [0.35, 0.0], 0.0),
    ],
    "F": [
        ([-0.35, 0.0], [-0.35, 1.0], 0.0),
        ([-0.35, 1.0], [0.35, 1.0], 0.0),
        ([-0.35, 0.5], [0.25, 0.5], 0.0),
    ],
    "G": [
        ([-0.35, 0.35], [0.35, 0.35], -180.0),
        ([-0.35, 0.65], [0.247, 0.897], 135.0),
        ([-0.35, 0.35], [-0.35, 0.65], 0.0),
        ([0.35, 0.35], [0.35, 0.5], 0.0),
        ([0.1, 0.5], [0.35, 0.5], 0.0),
    ],
    "H": [
        ([-0.35, 0.0], [-0.35, 1.0], 0.0),
        ([0.35, 0.0], [0.35, 1.0], 0.0),
        ([-0.35, 0.5], [0.35, 0.5], 0.0),
    ],
    "I": [
        ([0.0, 0.0], [0.0, 1.0], 0.0),
        ([-0.15, 0.0], [0.15, 0.0], 0.0),
        ([-0.15, 1.0], [0.15, 1.0], 0.0),
    ],
    "J": [
        ([0.15, 0.15], [0.15, 1.0], 0.0),
        ([0.15, 0.15], [-0.15, 0.15], 180.0),
    ],
    "K": [
        ([-0.35, 0.0], [-0.35, 1.0], 0.0),
        ([-0.35, 0.5], [0.35, 1.0], 0.0),
        ([-0.35, 0.5], [0.35, 0.0], 0.0),
    ],
    "L": [
        ([-0.35, 0.0], [-0.35, 1.0], 0.0),
        ([-0.35, 0.0], [0.35, 0.0], 0.0),
    ],
    "M": [
        ([-0.35, 0.0], [-0.35, 1.0], 0.0),
        ([-0.35, 1.0], [0.0, 0.5], 0.0),
        ([0.0, 0.5], [0.35, 1.0], 0.0),
        ([0.35, 1.0], [0.35, 0.0], 0.0),
    ],
    "N": [
        ([-0.35, 0.0], [-0.35, 1.0], 0.0),
        ([-0.35, 1.0], [0.35, 0.0], 0.0),
        ([0.35, 0.0], [0.35, 1.0], 0.0),
    ],
    "O": [
        ([-0.35, 0.35], [0.35, 0.35], -180.0),
        ([-0.35, 0.65], [0.35, 0.65], 180.0),
        ([-0.35, 0.35], [-0.35, 0.65], 0.0),
        ([0.35, 0.35], [0.35, 0.65], 0.0),
    ],
    "P": [
        ([-0.35, 0.0], [-0.35, 1.0], 0.0),
        ([-0.35, 1.0], [0.1, 1.0], 0.0),
        ([-0.35, 0.5], [0.1, 0.5], 0.0),
        ([0.1, 1.0], [0.1, 0.5], 180.0),
    ],
    "Q": [
        ([-0.35, 0.35], [0.35, 0.35], -180.0),
        ([-0.35, 0.65], [0.35, 0.65], 180.0),
        ([-0.35, 0.35], [-0.35, 0.65], 0.0),
        ([0.35, 0.35], [0.35, 0.65], 0.0),
        ([0.0, 0.35], [0.35, 0.0], 0.0),
    ],
    "R": [
        ([-0.35, 0.0], [-0.35, 1.0], 0.0),
        ([-0.35, 1.0], [0.1, 1.0], 0.0),
        ([-0.35, 0.5], [0.1, 0.5], 0.0),
        ([0.1, 1.0], [0.1, 0.5], 180.0),
        ([0.0, 0.5], [0.35, 0.0], 0.0),
    ],
    "S": [
        ([-0.35, 0.0], [0.1, 0.0], 0.0),
        ([0.1, 0.0], [0.1, 0.5], -180.0),
        ([-0.1, 0.5], [0.1, 0.5], 0.0),
        ([-0.1, 0.5], [-0.1, 1.0], 180.0),
        ([-0.1, 1.0], [0.35, 1.0], 0.0),
    ],
    "T": [
        ([0.0, 0.0], [0.0, 1.0], 0.0),
        ([-0.35, 1.0], [0.35, 1.0], 0.0),
    ],
    "U": [
        ([-0.35, 0.35], [0.35, 0.35], -180.0),
        ([-0.35, 0.35], [-0.35, 1.0], 0.0),
        ([0.35, 0.35], [0.35, 1.0], 0.0),
    ],
    "V": [
        ([-0.35, 1.0], [0.0, 0.0], 0.0),
        ([0.35, 1.0], [0.0, 0.0], 0.0),
    ],
    "W": [
        ([-0.35, 1.0], [-0.15, 0.0], 0.0),
        ([-0.15, 0.0], [0.0, 0.65], 0.0),
        ([0.15, 0.0], [0.0, 0.65], 0.0),
        ([0.35, 1.0], [0.15, 0.0], 0.0),
    ],
    "X": [
        ([-0.35, 0.0], [0.35, 1.0], 0.0),
        ([0.35, 0.0], [-0.35, 1.0], 0.0),
    ],
    "Y": [
        ([-0.35, 1.0], [0.0, 0.5], 0.0),
        ([0.35, 1.0], [0.0, 0.5], 0.0),
        ([0.0, 0.5], [0.0, 0.0], 0.0),
    ],
    "Z": [
        ([-0.35, 1.0], [0.35, 1.0], 0.0),
        ([0.35, 1.0], [-0.35, 0.0], 0.0),
        ([-0.35, 0.0], [0.35, 0.0], 0.0),
    ],
    "0": [
        ([-0.15, 0.06], [0.15, 0.06], -105.0),
        ([-0.15, 0.06], [-0.15, 0.94], 60.0),
        ([-0.15, 0.94], [0.15, 0.94], 105.0),
        ([0.15, 0.06], [0.15, 0.94], -60.0),
    ],
    "1": [
        ([0.0, 0.0], [0.0, 1.0], 0.0),
        ([-0.15, 0.0], [0.15, 0.0], 0.0),
        ([-0.2, 0.8], [0.0, 1.0], 0.0),
    ],
    "2": [
        ([-0.25, 0.75], [0.177, 0.573], 225.0),
        ([0.177, 0.573], [-0.25, 0.0], 0.0),
        ([-0.25, 0.0], [0.25, 0.0], 0.0),
    ],
    "3": [
        ([-0.25, 1.0], [0.0, 1.0], 0.0),
        ([0.0, 1.0], [0.0, 0.5], 180.0),
        ([-0.15, 0.5], [0.0, 0.5], 0.0),
        ([0.0, 0.5], [0.0, 0.0], 180.0),
        ([-0.25, 0.0], [0.0, 0.0], 0.0),
    ],
    "4": [
        ([-0.25, 1.0], [-0.25, 0.5], 0.0),
        ([-0.25, 0.5], [0.25, 0.5], 0.0),
        ([0.25, 1.0], [0.25, 0.0], 0.0),
    ],
    "5": [
        ([-0.25, 1.0], [0.25, 1.0], 0.0),
        ([-0.25, 1.0], [-0.25, 0.6], 0.0),
        ([-0.25, 0.6], [0.25, 0.25], 110.0),
        ([0.25, 0.25], [-0.25, 0.25], 180.0),
    ],
    "6": [
        ([0.25, 1.0], [-0.25, 0.25], -66.5),
        ([-0.25, 0.25], [0.25, 0.25], 180.0),
        ([-0.25, 0.25], [0.25, 0.25], -180.0),
    ],
    "7": [
        ([-0.25, 1.0], [0.25, 1.0], 0.0),
        ([0.25, 1.0], [-0.25, 0.0], 0.0),
    ],
    "8": [
        ([-0.25, 0.75], [0.25, 0.75], 180.0),
        ([-0.25, 0.75], [0.25, 0.75], -180.0),
        ([-0.25, 0.25], [0.25, 0.25], 180.0),
        ([-0.25, 0.25], [0.25, 0.25], -180.0),
    ],
    "9": [
        ([-0.25, 0.75], [0.25, 0.75], 180.0),
        ([-0.25, 0.75], [0.25, 0.75], -180.0),
        ([0.25, 0.75], [-0.25, 0.0], 66.5),
    ],
    ".": [([0.0, 0.0], [0.0, 0.0], 0.0)],
    "!": [
        ([0.0, 0.0], [0.0, 0.0], 0.0),
        ([0.0, 1.0], [0.0, 0.25], 0.0),
    ],
    "?": [
        ([0.0, 0.0], [0.0, 0.0], 0.0),
        ([-0.25, 0.75], [0.177, 0.573], 225.0),
        ([0.177, 0.573], [0.0, 0.323], -45.0),
        ([0.0, 0.323], [0.0, 0.25], 0.0),
    ],
    " ": [],
}


class Letter(Lineart2D):
    def __init__(self, char, pos, angle, size, color):
        super(Letter, self).__init__()
        if char in letters:
            segs = letters[char]
            for seg in segs:
                self.add_segment(*seg)
        self.color = color
        self.off = [-pos[0], -pos[1]]
        ca = m.cos(angle * m.pi / 180.0) / size
        sa = m.sin(angle * m.pi / 180.0) / size
        self.mat = [[ca, sa], [-sa, ca]]


# Example scenes


class MutatingShapeScene(Scene):
    def __init__(self, ctr):
        super(MutatingShapeScene, self).__init__(ctr)
        self.corners = 4
        self.rot = 0.0
        self.goalrot = random() - 0.5
        self.ratiof = 0.0
        self.goalratiof = random() * 0.8
        self.radius = 0.5
        self.cm = ColorMeander()
        self.shape = Star(
            self.corners, (0, 0), 0.0, self.radius, self.radius, self.cm.get()
        )
        self.add_shape(self.shape)

    def update(self, step):
        # Color
        self.cm.step()
        self.shape.color = self.cm.get()
        # Corners
        if random() < 0.02:
            if random() < (self.corners - 2) / 6.0:
                self.corners -= 1
            else:
                self.corners += 1
            self.shape.num = self.corners
        # Rotation
        if self.goalrot - self.rot > 0.0:
            self.rot += 0.01
            if self.rot > self.goalrot:
                self.goalrot = random() - 0.5
        else:
            self.rot -= 0.01
            if self.rot < self.goalrot:
                self.goalrot = random() - 0.5
        self.shape.set_torque(360.0 / 20.0 * self.rot)
        # Ratio
        if self.goalratiof - self.ratiof > 0.0:
            self.ratiof += 0.01
            if self.ratiof > self.goalratiof:
                self.goalratiof = random() * 0.8
        else:
            self.ratiof -= 0.01
            if self.ratiof < self.goalratiof:
                self.goalratiof = random() * 0.8
        self.shape.set_radius(
            self.radius * (1.0 + self.ratiof), self.radius * (1.0 - self.ratiof)
        )
        # Angle
        self.shape.update(step)


class MovingShapesScene(Scene):
    def __init__(self, ctr):
        super(MovingShapesScene, self).__init__(ctr)
        self.time = 0
        self.crtime = 0
        self.freq = 0.5
        self.horizon = self.preferred_fps * 20
        self.replay = False
        self.record = False
        self.pre_shapes = []
        self.colorfunc = random_hsl_color_func(sat=[0.5,1.0], light=0.0)

    def create(self):
        # slumpa ut form, färg, hastighet, rotation, riktning, offset från centrum, (djup)
        col = self.colorfunc() # hsl_color(random(), 0.6 + 0.4*random(), 0.0)
        speed = m.exp((random() - 0.5) * 1.1) / (self.preferred_fps * 6.0)
        rot = (random() - 0.5) * 360.0 / self.preferred_fps * 0.1
        angle = random() * 2 * m.pi
        offset = (random() - 0.5) * 1.6
        vec = (m.sin(angle), m.cos(angle))
        cent = (-vec[0] * 1.5 + vec[1] * offset, -vec[1] * 1.5 - vec[0] * offset)
        vel = (vec[0] * speed, vec[1] * speed)
        nstep = int(3.0 / speed)
        sp = int(random() * (2 + 4 + 5))
        if sp == 0:  # circle
            sizef = random() * 0.8 + 0.1
            shape = Ellipse(cent, 0.0, sizef*0.5, sizef*0.5, col)
        elif sp == 1:  # ellipse
            ratiof = random() * 0.8
            shape = Ellipse(cent, 0.0, (1.0 + ratiof) * 0.25, (1.0 - ratiof) * 0.25, col)
        elif sp < 6:  # Polygon
            corners = sp + 1
            sizef = random() * 0.8 + 0.1
            shape = Polygon(corners, cent, 0.0, sizef*0.5, col)
        else:  # Star
            corners = sp - 4
            ratiof = random() * 0.8
            shape = Star(
                corners, cent, 0.0, (1.0 + ratiof) * 0.25, (1.0 - ratiof) * 0.25, col
            )
        shape.set_speed(vel[0], vel[1])
        shape.set_torque(rot)
        shape.duetime = self.time + nstep
        return shape

    def reset(self, numframes):
        if numframes and self.horizon:
            self.time = -self.horizon
            self.crtime = self.time
            self.record = True
            while self.time < 0:
                self.update(1)
            self.record = False
        else:
            self.time = 0
            self.crtime = 0
            self.replay = False
            self.record = False

    def update(self, step):
        for sh in reversed(self.shapes):
            if sh.duetime < self.time:
                self.shapes.remove(sh)
        if self.time >= self.crtime:
            if self.record:
                sh = self.create()
                self.add_shape(copy(sh))
                sh.duetime += self.preferred_frames
                self.crtime = self.time + int(-m.log(random()*0.94 + 0.03) / self.freq * self.preferred_fps)
                self.pre_shapes.append((self.crtime + self.preferred_frames, sh))
            elif self.replay:
                if self.pre_shapes:
                    self.add_shape(self.pre_shapes[0][1])
                    self.crtime = self.pre_shapes[0][0]
                    self.pre_shapes = self.pre_shapes[1:]
            else:
                self.add_shape(self.create())
                self.crtime = self.time + int(-m.log(random()*0.94 + 0.03) / self.freq * self.preferred_fps)
                if self.pre_shapes and self.crtime >= self.pre_shapes[0][0]:
                    self.replay = True
        super(MovingShapesScene, self).update(step)
        self.time += step


class CaleidoScene(MovingShapesScene):
    def __init__(self, ctr, sym):
        super(CaleidoScene, self).__init__(ctr)
        self.freq = 0.6
        self.symang = m.pi / sym

    def create(self):
        # slumpa ut form, färg, hastighet, rotation, riktning, offset från centrum, (djup)
        col = hsl_color(random(), 1.0, 0.0)
        speed = m.exp((random() - 0.5) * 2.3) / 20.0 * 0.1
        rot = (random() - 0.5) * 360.0 / 20.0 * 0.3
        angle = random() * 2 * m.pi
        offset = random() - 0.5
        vec = (m.sin(angle), m.cos(angle))
        cent = (-vec[0] * 1.5 + vec[1] * offset, -vec[1] * 1.5 - vec[0] * offset + 0.5)
        vel = (vec[0] * speed, vec[1] * speed)
        nstep = int(3.0 / speed)
        sp = int(random() * (2 + 4 + 5))
        if sp == 0:  # circle
            sizef = random() * 0.8 + 0.1
            shape = Ellipse(cent, 0.0, sizef, sizef, col)
        elif sp == 1:  # ellipse
            ratiof = random() * 0.8
            shape = Ellipse(cent, 0.0, (1.0 + ratiof) * 0.5, (1.0 - ratiof) * 0.5, col)
        elif sp < 6:  # Polygon
            corners = sp + 1
            sizef = random() * 0.8 + 0.1
            shape = Polygon(corners, cent, 0.0, sizef, col)
        else:  # Star
            corners = sp - 4
            ratiof = random() * 0.8
            shape = Star(
                corners, cent, 0.0, (1.0 + ratiof) * 0.5, (1.0 - ratiof) * 0.5, col
            )
        shape.set_speed(vel[0], vel[1])
        shape.set_torque(rot)
        shape.duetime = self.time + nstep
        return shape

    def get_color(self, coord):
        r = m.sqrt(coord[0] ** 2 + coord[1] ** 2)
        a = m.atan2(coord[1], coord[0])
        a = abs((a % (2 * self.symang)) - self.symang)
        return super(CaleidoScene, self).get_color((m.sin(a) * r, m.cos(a) * r))


class BouncingScene(MovingShapesScene):
    def __init__(self, ctr, num):
        super(BouncingScene, self).__init__(ctr)
        for i in range(num):
            self.create()

    def create(self):
        cent = (gauss(0.0, 0.2), gauss(0.0, 0.2))
        shape = Blob(cent, 0.12, random_hsl_color_func(light=0.0)())
        shape.speed = (gauss(0.0, 0.1), gauss(0.0, 0.1))
        return shape

    def dot(self, v1, v2):
        return sum(map(lambda x1, x2: x1 * x2, v1, v2))

    def scale(self, v1, sc):
        return tuple(map(lambda x1: x1 * sc, v1))

    def add(self, v1, v2):
        return tuple(map(lambda x1, x2: x1 + x2, v1, v2))

    def update(self, step):
        # om utanför, vänd håll med slumpbrus
        for sh in self.shapes:
            if self.dot(sh.cent, sh.cent) > 1.0 and self.dot(sh.cent, sh.speed) > 0.0:
                delta = self.dot(sh.cent, sh.speed) / self.dot(sh.cent, sh.cent)
                sh.speed = self.add(sh.speed, self.scale(sh.cent, -2 * delta))
        super(BouncingScene, self).update(step)


# ---------------------------------------------------------

