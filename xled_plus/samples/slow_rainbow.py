# Preview: https://github.com/aioue/twinkly-c120/blob/main/preview.gif

"""
slow_rainbow

A rainbow that drifts slowly along the string. One revolution takes 120 seconds.

Two rainbows are spread over the LED index. With two strings leaving the
controller in the same direction, the strings show the same colours at the same
time. With the strings in opposite directions, new colours appear at the
controller and move out along both strings. Set CIRCULAR = True for that
layout to get one continuous rainbow along the whole stretch instead.

The colours are plain full-saturation HSV, which shows blue more strongly than
the other colours. Set BALANCED = True to use hsl_color, which compensates for
the LED colour balance.

Tested on a TWS250SPP2 with both strings in the same direction.

Contributed by Tom Paine
"""

from colorsys import hsv_to_rgb

from xled_plus.samples.sample_setup import *

CIRCULAR = False
BALANCED = False

SECONDS = 120
# 18 fps is higher than the 12 or less that suits slow patterns in general.
# On a TWS250SPP2, stepping was visible at 12 fps over this revolution time.
FPS = 18
FRAMES = SECONDS * FPS
RAINBOWS = 2


def rainbow_color(index, led_count, frame):
    hue = (RAINBOWS * index / led_count - frame / FRAMES) % 1.0
    if BALANCED:
        return hsl_color(hue, 1.0, 0.0)
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
        lambda t: ctr.make_func_pattern(
            lambda i: rainbow_color(i, ctr.num_leds, t),
            circular=CIRCULAR,
        ),
    ),
    FPS,
    "slow_rainbow",
)
