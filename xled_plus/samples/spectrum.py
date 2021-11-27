from .sample_setup import *


ctr = setup_control()
ctr.show_movie(
    ctr.make_func_movie(
        120,
        lambda t: ctr.make_layout_pattern(
            lambda pos: hsl_color((pos[1] - t / 120.0) % 1.0, 1.0, 0.0)
        ),
    ),
    8,
)
