"""
xled_plus.shapes
~~~~~~~~~~~~~~~~

Author: Anders Holst (anders.holst@ri.se), 2021

This module contains classes for creating scenes of moving (or still) objects.
Objects implemented are various geometrical shapes, such as polygons, stars,
and circles, but also simple letters and numbers. 
"""


import math as m
from random import random, gauss, uniform
from copy import copy

from xled_plus.ledcolor import hsl_color
from xled_plus.effect_base import Effect
from xled_plus.colormeander import ColorMeander
from xled_plus.pattern import random_hsl_color_func, dimcolor



class Scene(Effect):
    def __init__(self, ctr):
        super(Scene, self).__init__(ctr)
        self.shapes = []
        self.occvec = [False] * ctr.num_leds
        self.bgfunc = False
        self.proj2D3D = False  # 'cylshell', 'cylbase', 'halfsphere' 

    def add_shape(self, sh):
        self.shapes.append(sh)
        self.shapes.sort(key=lambda sh: sh.depth)

    def remove_shape(self, sh):
        self.shapes.remove(sh)

    def update(self, step):
        for sh in self.shapes:
            sh.update(step)

    def blend_colors(self, colors):
        if colors:
            return tuple(map(lambda *args: int(round(sum(args) / len(args))), *colors))
        else:
            return False

    def get_color(self, coord, ind):
        goaldepth = False
        colors = []
        for sh in self.shapes:
            if goaldepth and sh.depth != goaldepth:
                break
            else:
                col = sh.get_color(coord, ind)
                if col:
                    if not goaldepth:
                        goaldepth = sh.depth
                    colors.append(col)
        self.occvec[ind] = True if colors else False
        return self.blend_colors(colors) or (self.bgfunc(coord, ind) if self.bgfunc else (0, 0, 0))

    def reset(self, numframes):
        pass

    def getnext(self):
        self.update(1)
        dim = self.ctr.get_layout_bounds()["dim"]
        if dim == 3 and self.proj2D3D:
            if self.proj2D3D == "cylbase":
                fact = self.ctr.get_layout_bounds()["radius"] / self.ctr.get_layout_bounds()["cylradius"]
                colfunc = lambda pos, ind: self.get_color((pos[0]*fact, pos[2]*fact), ind)
                return self.ctr.make_layout_pattern(colfunc, style="centered", index=True)
            elif self.proj2D3D == "cylshell":
                hyp = ((m.pi * self.ctr.get_layout_bounds()["cylradius"]) ** 2 + 0.25) ** 0.5
                xfact = m.pi / 180.0 * self.ctr.get_layout_bounds()["cylradius"] / hyp
                yfact = 1.0 / hyp
                colfunc = lambda pos, ind: self.get_color((pos[1]*xfact, (pos[2] - 0.5)*yfact), ind)
                return self.ctr.make_layout_pattern(colfunc, style="cylinder", index=True)
            elif self.proj2D3D == "halfsphere":
                colfunc = lambda pos, ind: self.get_color((m.sin(pos[1]*m.pi/180.0)*pos[2]/90.0, -m.cos(pos[1]*m.pi/180.0)*pos[2]/90.0), ind)
                return self.ctr.make_layout_pattern(colfunc, style="halfsphere", index=True)
        return self.ctr.make_layout_pattern(self.get_color, style="centered", index=True)

    def getoccupancy(self):
        return self.occvec

    def get_scene_bounds(self):
        bounds = self.ctr.get_layout_bounds()
        if bounds["dim"] == 3:
            if self.proj2D3D == "cylbase":
                fact = self.ctr.get_layout_bounds()["radius"] / self.ctr.get_layout_bounds()["cylradius"]
                return [(fact * bounds["bounds"][0][0], fact * bounds["bounds"][0][1]),
                        (fact * bounds["bounds"][2][0], fact * bounds["bounds"][2][1])]
            elif self.proj2D3D == "cylshell":
                hyp = ((m.pi * bounds["cylradius"]) ** 2 + 0.25) ** 0.5
                xfact = m.pi * bounds["cylradius"] / hyp
                yfact = 0.5 / hyp
                return [(-xfact, xfact), (-yfact, yfact)]
            elif self.proj2D3D == "halfsphere":
                return [(-1.0, 1.0), (-1.0, 1.0)]
            else:
                return bounds["bounds"]
        elif bounds["dim"] == 2:
            fact = 1.0 / bounds["radius"]
            return [(fact * bounds["bounds"][0][0], fact * bounds["bounds"][0][1]),
                    (fact * bounds["bounds"][1][0], fact * bounds["bounds"][1][1])]
        else:
            return bounds["bounds"]


class Shape(object):
    def __init__(self, cent, angle):
        self.depth = 0
        self.color = False
        self.cent = cent
        self.speed = (0.0, ) * len(cent)
        self.angle = angle * m.pi / 180.0
        self.torque = 0.0

    def is_inside(self, coord):
        pass

    def get_color(self, coord, ind):
        if self.is_inside(coord):
            return self.color(coord, ind) if callable(self.color) else self.color
        else:
            return False

    def set_depth(self, depth):
        self.depth = depth

    def set_speed(self, vx, vy):
        self.speed = (vx, vy)

    def set_torque(self, va):
        self.torque = va * m.pi / 180.0

    def update(self, step):
        self.cent = tuple(map(lambda c, s: c + step * s, self.cent, self.speed))
        self.angle = (self.angle + step * self.torque) % 360.0


class Blob(Shape):
    def __init__(self, cent, rad, col):
        super(Blob, self).__init__(cent, 0.0)
        self.rad = rad
        self.color = col

    def is_inside(self, coord):
        return (
            sum(map(lambda x1, x2: (x1 - x2) ** 2, self.cent, coord)) <= self.rad ** 2
        )

    def get_color(self, coord, ind):
        dist = (
            m.sqrt(sum(map(lambda x1, x2: (x1 - x2) ** 2, self.cent, coord))) / self.rad
        )
        if dist > 1.0:
            return False
        else:
            col = self.color(coord, ind) if callable(self.color) else self.color
            return dimcolor(col, 1.0 - dist)


class Polygon(Shape):
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


class Ellipse(Shape):
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


class Star(Shape):
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
        super(Lineart2D, self).__init__((0.0, 0.0), 0.0)
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


class RunningText(MovingShapesScene):
    def __init__(self, ctr, txt, color, linewidth=0.1, size=0.6, speed=1.0):
        super(RunningText, self).__init__(ctr)
        self.textcolor = color
        self.lw = linewidth
        self.txt = txt
        self.size = size
        self.speed = speed
        self.horizon = 0
        self.proj2D3D = "cylshell"
        self.place_text()
        self.preferred_frames = self.nsteps

    def set_fps(self, fps):
        self.preferred_fps = fps
        self.place_text()
        self.preferred_frames = self.nsteps
        
    def place_text(self):
        bounds = self.get_scene_bounds()
        # Size is relative the total height of leds, convert to relative radius
        size = self.size * (bounds[1][1] - bounds[1][0])
        # Speed is in letter heights per second, convert to length per step
        speed = size * self.speed / self.preferred_fps
        self.currx = bounds[0][1]
        self.endx = bounds[0][0]
        self.liney = -size / 2.0
        self.shapes = []
        for ind, ch in enumerate(self.txt):
            if isinstance(self.textcolor, list):
                col = self.textcolor[ind % len(self.textcolor)]
            elif callable(self.textcolor):
                col = self.textcolor(ind)
            else:
                col = self.textcolor
            sh = Letter(ch, (0, self.liney), 0, size, col)
            sh.lw = self.lw
            sh.off[0] = -self.currx + (sh.extent[0] - sh.lw * 0.5) * size
            sh.set_speed(-speed, 0.0)
            wdt = max(0.4, sh.extent[2] - sh.extent[0] + 2 * sh.lw)
            self.currx += wdt * size
            self.add_shape(sh)
        self.nsteps = int(round((self.currx - self.endx) / speed + 0.5))
        self.time = 0

    def reset(self, numframes):
        if self.time != 0:
            self.place_text()

    def update(self, step):
        for sh in self.shapes:
            sh.update(step)
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

    def get_color(self, coord, ind):
        r = m.sqrt(coord[0] ** 2 + coord[1] ** 2)
        a = m.atan2(coord[1], coord[0])
        a = abs((a % (2 * self.symang)) - self.symang)
        return super(CaleidoScene, self).get_color((m.sin(a) * r, m.cos(a) * r), ind)


class BouncingScene(MovingShapesScene):
    def __init__(self, ctr, num, speed=0.25, size=0.3, colorfunc=False):
        super(BouncingScene, self).__init__(ctr)
        self.bounds = ctr.get_layout_bounds()
        self.size = size
        self.speed = speed
        self.colfunc = colorfunc or random_hsl_color_func(light=0.0)
        for i in range(num):
            self.ind = i
            self.add_shape(self.create())

    def create(self):
        cent = tuple(uniform(*self.bounds["bounds"][d]) for d in range(self.bounds["dim"]))
        vec = tuple(gauss(0.0, 0.1) for d in range(self.bounds["dim"]))
        vlen = self.dot(vec, vec) ** 0.5
        shape = Blob(cent, self.size/2.0, self.colfunc(self.ind))
        shape.speed = tuple(ele/vlen * self.speed/self.preferred_fps for ele in vec)
        return shape

    def dot(self, v1, v2):
        return sum(map(lambda x1, x2: x1 * x2, v1, v2))

    def scale(self, v1, sc):
        return tuple(map(lambda x1: x1 * sc, v1))

    def add(self, v1, v2):
        return tuple(map(lambda x1, x2: x1 + x2, v1, v2))

    def bounces(self, sh):
        rad = self.dot(sh.cent, sh.cent)
        dir = self.dot(sh.cent, sh.speed)
        if rad > 1.0 and dir > 0.0:
            return True
        for d in range(self.bounds["dim"]):
            c = sh.cent[d] * self.bounds["radius"] + self.bounds["center"][d]
            if ((c < self.bounds["bounds"][d][0] and sh.speed[d] < 0.0) or
                (c > self.bounds["bounds"][d][1] and sh.speed[d] > 0.0)):
                return True
        if self.bounds["dim"] == 3:
            vec = (sh.cent[0], sh.cent[2])
            sp = (sh.speed[0], sh.speed[2])
            rad = self.dot(vec, vec) ** 0.5
            dir = self.dot(vec, sp)
            if rad * self.bounds["radius"] > self.bounds["cylradius"] and dir > 0.0:
                return True
        return False

    def update(self, step):
        for sh in self.shapes:
            if self.bounces(sh):
                vec = tuple(c + gauss(0.0, 0.1) for c in sh.cent)
                vlen2 = self.dot(vec, vec)
                delta = self.dot(vec, sh.speed) / vlen2
                sh.speed = self.add(sh.speed, self.scale(vec, -2 * delta))
            sh.update(step)


# ---------------------------------------------------------

