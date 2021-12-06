"""
Day 7 - Breathing selected colors

And then an attempt to mimic a pattern from the app again. This is actually
more similar to the Glow effect on the app than the Day 2 example: Each led
stays the same hue but varies in brightness. The hues are picked from a fixed
list. Differences from Glow on the app are: The color positions are random and
not regular, and (just as in the Day 2 example) a smooth transition to the
first frame. 

You can select other colors by changing the cols list below. A second example
is provided, remove the # in front of the line to see it. Colors are given as
(hue, saturation, lightness) where hue and saturation has range [0, 1] and
lightness range [-1, 1] where -1 is black, +1 is white, and 0 the most colored.
"""

from xled_plus.samples.sample_setup import *

ctr = setup_control()
cols = [(0.375, 1.0, 0.0), (0.58, 1.0, 0.0), (0.375, 1.0, 0.3), (0.29, 1.0, 0.0)]
# cols = [(0.72, 1.0, 0.15), (0.89, 1.0, 0.0), (0.05, 1.0, 0.05), (0.0, 1.0, 0.8)]
BreathCP(ctr, cols).launch_movie()
