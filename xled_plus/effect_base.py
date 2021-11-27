"""
xled_plus.effect_base
~~~~~~~~~~~~~~~~~

Author: Anders Holst (anders.holst@ri.se), 2021

Base class Effect to provide a consistent interface to moving effects.
As outer API, i.e to users of an effect, it provides these functions:
'launch_movie()' to create a movie of the effect and upload and start playing it.
'save_movie()' to create a movie of the effect and save it to file for later use.
'launch_rt()' for playing the effect in real time.
'stop_rt()' for stopping the currently played real time effect.

As inner API, i.e for communicating with its subclasses, it requires each subclass
to provide two functions:
'reset(numframes)' to prepare all inner data structures to start generating an effect.
'getnext()' to produce and return the next frame pattern of the effect.
The Effect class also provides two member variables that can be set by the subclass:
'preferred_frames' and 'preferred_fps', as a sitable number of frames in a movie
of the effect, and the suggested number of frames per second of the effect.
Note that the 'reset(numframes)' function will either get the number of frames
required for the movie (then typically the same as 'preferred_frames') or False
if a real time effect is requested. If there is a non-False numframes, 'reset'
should try to set up data structures to make sure that after this many frames
the movie will seamlessly return to the first frame.
"""

import sys
import time

if sys.version_info.major == 2:
    from threading import _Timer

    TimerX = _Timer
else:
    from threading import Timer

    TimerX = Timer


class RepeatedTimer(TimerX):
    def run(self):
        lasttime = time.time()
        self.function(*self.args, **self.kwargs)
        while not self.finished.wait(
            max(0.0, self.interval - (time.time() - lasttime))
        ):
            lasttime = time.time()
            self.function(*self.args, **self.kwargs)


effect_timer = None


class Effect(object):
    def __init__(self, ctr):
        self.ctr = ctr
        self.preferred_frames = 120
        self.preferred_fps = 8

    def reset(self, numframes=False):
        pass  # provided by subclass

    def getnext(self):
        pass  # provided by subclass

    def launch_rt(self):
        global effect_timer

        def doit():
            self.ctr.show_rt_frame(self.getnext())

        if effect_timer:
            effect_timer.cancel()
        effect_timer = RepeatedTimer(1.0 / self.preferred_fps, doit)
        self.reset(False)
        effect_timer.start()
        return True

    def stop_rt(self):
        global effect_timer
        if effect_timer:
            effect_timer.cancel()
        effect_timer = None

    def make_movie(self, numframes):
        frames = []
        self.reset(numframes)
        for i in range(numframes):
            frames.append(self.getnext())
        return self.ctr.to_movie(frames)

    def launch_movie(self):
        self.stop_rt()
        self.ctr.show_movie(self.make_movie(self.preferred_frames), self.preferred_fps)

    def save_movie(self, name):
        self.ctr.save_movie(
            name, self.make_movie(self.preferred_frames), self.preferred_fps
        )


def stop_rt():
    global effect_timer
    if effect_timer:
        effect_timer.cancel()
        effect_timer = None
