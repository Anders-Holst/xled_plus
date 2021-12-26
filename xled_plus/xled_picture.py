"""
xled_plus.xled_picture
~~~~~~~~~~~~~~~~~~~~~~

Author: Anders Holst (anders.holst@ri.se), 2021

An effect that shows a picture (possibly animated) on your leds.
The PictureEffect object takes as parameters: the HighControlInterface
for the leds, the full filename of the picture, and optionally a
parameter `fit` which can be: 'stretch' (for stretching the axes to fit
the layout bounds), 'small' (to fit the entire picture inside the layout,
leaving black edges), 'large' (to fill up the entire layout, truncating
parts that does not fit), and 'medium' (which is a geometrical average
between small and large). 'stretch' is the default.
If the picture is an animated gif, it will become a move, otherwise it is
a static effect.

It can be invoked from the shell as:
`python -m xled_plus.xled_picture [host] filename`
where [host] is an optional ip number of the leds.

This module uses the Python Image Processing Library (pillow), to read
the picture from file.
"""

from PIL import Image
from xled_plus.effect_base import Effect
from xled_plus.ledcolor import image_to_led_rgb
from xled_plus.highcontrol import HighControlInterface
from xled.discover import discover
import sys


class PictureEffect(Effect):
    def __init__(self, ctr, fname, fit='stretch'):
        # fit can be: 'stretch', 'small', 'large', 'medium'
        super(PictureEffect, self).__init__(ctr)
        self.im = Image.open(fname)
        self.xmid = (self.im.size[0]-1) / 2.0
        self.ymid = (self.im.size[1]-1) / 2.0
        if fit == 'stretch':
            self.xscale = self.im.size[0]-1
            self.yscale = self.im.size[1]-1
        else:
            bounds = ctr.get_layout_bounds()
            xdiff = bounds["bounds"][0][1] - bounds["bounds"][0][0]
            if xdiff == 0.0:
                xdiff = 1.0
            if fit == 'small':
                fact = max((self.im.size[0]-1) / xdiff, self.im.size[1]-1)
            elif fit == 'large':
                fact = min((self.im.size[0]-1) / xdiff, self.im.size[1]-1)
            else:
                fact = ((self.im.size[0]-1) * (self.im.size[0]-1) / xdiff) ** 0.5
            self.xscale = xdiff * fact
            self.yscale = fact
        if "is_animated" in dir(self.im) and self.im.is_animated:
            self.preferred_fps = 100.0 / self.im.info["duration"]
            self.preferred_frames = self.im.n_frames
        else:
            self.preferred_fps = 1
            self.preferred_frames = 1

    def get_color(self, pos):
        coord = (int(round((pos[0] - 0.5) * self.xscale + self.xmid)),
                 int(round((0.5 - pos[1]) * self.yscale + self.ymid)))
        if coord[0] >= 0 and coord[0] < self.im.size[0] and coord[1] >= 0 and coord[1] < self.im.size[1]:
            if self.im.mode == 'P':
                pix = self.im.getpixel(coord)
                rgb = self.im.getpalette()[pix*3:pix*3+3]
            elif self.im.mode == 'L':
                rgb = [self.im.getpixel(coord)] * 3
            else:
                rgb = self.im.getpixel(coord)[0:3]
        else:
            rgb = (0, 0, 0)
        return image_to_led_rgb(*rgb)

    def reset(self, numframes):
        self.index = -1

    def getnext(self):
        if "is_animated" in dir(self.im) and self.im.is_animated:
            self.index += 1
            self.im.seek(self.index % self.im.n_frames)
        return self.ctr.make_layout_pattern(self.get_color, style="square")


if __name__ == '__main__' and len(sys.argv) > 1:

    if sys.argv[1].replace(".","").isdigit() and len(sys.argv) > 2:
        host = sys.argv[1]
        file = sys.argv[2]
    else:
        host = discover().ip_address
        file = sys.argv[1]
    ctr = HighControlInterface(host)
    PictureEffect(ctr, file).launch_movie()
