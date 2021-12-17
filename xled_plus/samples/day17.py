"""
Day 17 - Sunset

Yesterday I complained about the ugly "Sunset" effect in the app.
This is my take on the theme Sunset.
"""

from xled_plus.samples.sample_setup import *

colpairs = [
    (0, (0.0571, 1.0000, 0.0352), (0.0571, 1.0000, 0.0352)),
    (40, (0.0571, 1.0000, 0.0352), (0.0571, 1.0000, 0.0352)),
    (80, (0.4658, 1.0000, 0.2203), (0.0571, 1.0000, 0.0352)),
    (120, (0.5315, 1.0000, -0.1719), (0.9008, 1.0000, 0.0871)),
    (140, (0.5674, 1.0000, -0.25), (0.9444, 1.0000, -0.2)),
    (160, (0.5874, 1.0000, -0.47), (0.6174, 1.0000, -0.25)),
    (200, (0.6174, 1.0000, -0.76), (0.6174, 1.0000, -0.95)),
    (240, (0.0, 1.0, -1.0), (0.0, 1.0, -1.0)),
    (260, (0.0, 1.0, -1.0), (0.0, 1.0, -1.0)),
    (280, (0.0571, 0.2000, -0.76), (0.0571, 1.0000, -0.95)),
    (300, (0.0571, 1.0000, 0.0352), (0.0571, 1.0000, 0.0352)),
]

lastt = -1
lastpair = None

def getpair(t):
    global lastt, lastpair
    if t != lastt:
        j = 0
        while colpairs[j][0] <= t:
            j += 1
        prop = float(t - colpairs[j-1][0]) / (colpairs[j][0] - colpairs[j-1][0])
        lastpair = (blendcolors(hsl_color(*colpairs[j-1][1]), hsl_color(*colpairs[j][1]), prop),
                    blendcolors(hsl_color(*colpairs[j-1][2]), hsl_color(*colpairs[j][2]), prop))
        lastt = t
    return lastpair

def gradient(t, pos):
    y = pos[1] if len(pos) > 1 else pos[0]
    pair = getpair(t)
    return blendcolors(pair[0], pair[1], y)

ctr = setup_control()
mov = ctr.make_func_movie(300, lambda t: ctr.make_layout_pattern(lambda pos: gradient(t, pos)))
ctr.show_movie(mov, 2)
