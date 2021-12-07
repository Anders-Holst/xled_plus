"""
xled_plus.xled_colorpicker
~~~~~~~~~~~~~~~~~~~~~~~~~~

This is an example application of the color picker for showing and
setting colors on the leds.

Create an XledColorPicker with a HighControlInterface as argument.
A window with a colored sphere will appear. Hover over the sphere
to watch colors. Click on a color to upload it to the leds as a movie.
Drag the surface of the sphere to rotate it.

When started from the shell, eg with 'python -m xled_plus.xled_colorpicker'
it will look on the netowork for any connected leds. If you know the
ip-address of your leds, you can provide it as an extra argument and it
will not have to search for it.
"""

from colorsphere.colorsphere import ColorPicker
from xled_plus.ledcolor import hsl_color, get_color_style, set_color_style
from xled_plus.highcontrol import HighControlInterface
from xled.discover import discover
import sys


class XledColorPicker:
    rtmode = False
    outermode = False
    printrgb = False
    printhsl = False
    noset = False

    def __init__(self, ctr):
        self.ctr = ctr

    def on_click(self, hsl, event):
        if hsl:
            if not self.noset:
                pat = self.ctr.make_solid_pattern(hsl_color(*hsl))
                id = self.ctr.upload_movie(self.ctr.to_movie(pat), 1, force=True)
                self.ctr.set_movies_current(id)
                self.outermode = 'movie'
            if self.printrgb and self.printhsl:
                args = hsl + (hsl_color(*hsl), )
                print("HSL: ({:.4f}, {:.4f}, {:.4f})  RGB: {}".format(*args))
            elif self.printrgb:
                print(hsl_color(*hsl))
            elif self.printhsl:
                print("({:.4f}, {:.4f}, {:.4f})".format(*hsl))

    def on_move(self, hsl, event):
        if hsl:
            if not self.rtmode:
                self.outermode = self.ctr.get_mode()['mode']
            pat = self.ctr.make_solid_pattern(hsl_color(*hsl))
            self.ctr.show_rt_frame(self.ctr.to_movie(pat))
            self.rtmode = True
        else:
            if self.rtmode:
                if self.outermode:
                    self.ctr.set_mode(self.outermode)
                self.rtmode = False

    def colorstyle_changed(self, style):
        if type(style) in [list, tuple]:
            for s in style:
                set_color_style(s)
        else:
            set_color_style(style)

    def exit_event_loop(self, *args):
        self.cp.win.fig.canvas.stop_event_loop()

    def set_color_style(self, style):
        self.cp.sphere.set_color_style(style)

    def launch(self, from_shell=False, printrgb=False, printhsl=False, noset=False):
        self.printrgb = printrgb
        self.printhsl = printhsl
        self.noset = noset
        self.cp = ColorPicker(self.on_click, self.on_move, name="Xled Color Picker")
        self.cp.sphere.set_color_style(get_color_style())
        self.cp.sphere.color_style_callbacks.append(self.colorstyle_changed)
        if from_shell:
            self.cp.win.add_close_callback(self.exit_event_loop)
            self.cp.win.fig.canvas.start_event_loop(0)


if __name__ == '__main__':

    noset = False
    rgb = False
    hsl = False
    host = False
    for arg in sys.argv:
        if arg == "noset":
            noset = True
        elif arg == "rgb":
            rgb = True
        elif arg == "hsl":
            hsl = True
        elif arg.replace(".","").isdigit():
            host = arg
    if not host:
        host = discover().ip_address
    ctr = HighControlInterface(host)
    XledColorPicker(ctr).launch(from_shell=True, printhsl=hsl, printrgb=rgb, noset=noset)
