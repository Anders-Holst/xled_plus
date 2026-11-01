# Preview: https://github.com/aioue/twinkly-c120/blob/main/preview.gif

"""
C.120

Two rainbows along the string. One pass takes 120 seconds:
2160 frames at 18 frames per second. The white channel stays off.
The movie bytes are full range. The original dimmer setting is 80%.

This uploads a stored movie. If it does not fit, xled_plus removes
the movies already on the device.

Contributed by Tom Paine
"""

from colorsys import hsv_to_rgb

from xled_plus.samples.sample_setup import *

FRAMES = 2160
FPS = 18
RAINBOWS = 2


def c120_color(index, led_count, frame):
    hue = (RAINBOWS * index / led_count - frame / FRAMES) % 1.0
    red, green, blue = hsv_to_rgb(hue, 1.0, 1.0)
    return (
        int(red * 255 + 0.5),
        int(green * 255 + 0.5),
        int(blue * 255 + 0.5),
    )


ctr = setup_control()
ctr.show_movie(
    ctr.make_func_movie(
        FRAMES,
        lambda t: ctr.make_layout_pattern(
            lambda pos, i: c120_color(i, ctr.num_leds, t),
            index=True,
        ),
    ),
    FPS,
    "C.120",
)
