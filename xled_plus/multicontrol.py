# -*- coding: utf-8 -*-

"""
xled_plus.multicontrol
~~~~~~~~~~~~~~~~~~~~~~

Handle multiple connected lights as one unit.
Create a MultiHighControlInterface by giving it a list of ip-addresses to
the devices that are connected, with the master device first. Then, use it
in the same way as a normal HighControlInterface.

"""

from __future__ import absolute_import

import io
import struct
import binascii
import time
import uuid

import struct
import base64

from xled.control import ControlInterface
from xled_plus.highcontrol import HighControlInterface


def pick_master_and_slaves(hostlst):
    ctrlst = [ControlInterface(ip) for ip in hostlst]
    master = False
    slaves = []
    for ctr in ctrlst:
        sync = ctr.get_led_movie_config()['sync']
        if sync['mode'] == 'master':
            assert not master, "Only one master device allowed in the group"
            master = ctr
        elif sync['mode'] == 'slave':
            slaves.append(ctr)
        else:
            assert len(hostlst) == 1, "One device does not belong to the group"
            master = ctr
    assert master, "No master device in the group"
    return master, slaves


class MultiHighControlInterface(HighControlInterface):
    """
    High level interface to control a group of joined devices in sync
    """

    def __init__(self, hostlst):
        master, slaves = pick_master_and_slaves(hostlst)
        super(MultiHighControlInterface, self).__init__(master.host)
        self.ctrlst = [master] + slaves
        info = self.get_device_info()
        self.family = info["fw_family"] if "fw_family" in info else "D"
        self.led_bytes = info["bytes_per_led"] if "bytes_per_led" in info else 3
        self.led_profile = info["led_profile"] if "led_profile" in info else "RGB"
        self.version = tuple(map(int, self.firmware_version()["version"].split(".")))
        self.nledslst = [ctr.get_device_info()["number_of_led"] for ctr in self.ctrlst]
        for ctr in slaves:
            ctr._udpclient = self.udpclient
        self.num_leds = sum(self.nledslst)
        self.string_config = [{'first_led_id': 0, 'length': self.num_leds}]
        self.layout = False
        self.layout_bounds = False
        self.last_mode = None
        self.last_rt_time = 0
        self.curr_mode = self.get_mode()["mode"]

    def split_movie(self, movie):
        # return a list of one movie per connected device
        lst = [io.BytesIO() for ctr in self.ctrlst]
        blens = [nleds * self.led_bytes for nleds in self.nledslst]
        totlen = self.num_leds * self.led_bytes
        num = movie.seek(0, 2) // totlen
        movie.seek(0)
        for i in range(num):
            for mov, blen in zip(lst, blens):
                mov.write(movie.read(blen))
        for mov in lst:
            mov.seek(0)
        return lst

    def show_movie(self, movie_or_id, fps=None, name=""):
        """
        Either starts playing an already uploaded movie with the provided id or name,
        or uploads a new movie and starts playing it at the provided frames-per-second,
        giving it the optional provided name.
        Note: if the movie do not fit in the remaining capacity, the old movie list is cleared.
        Switches to movie mode if necessary.
        The movie is an object suitable created with to_movie or make_func_movie.

        :param movie_or_id: either an integer id or a file-like object that points to movie
        :param fps: frames per second, or None if a movie id is given
        :param str name: name of uploaded movie
        """
        if isinstance(movie_or_id, int) and fps is None:
            if self.family == "D" or self.version < (2, 5, 6):
                if movie_or_id != 0:
                    return False
            else:
                movies = self.get_movies()["movies"]
                if movie_or_id in [entry["id"] for entry in movies]:
                    self.set_movies_current(movie_or_id)
                else:
                    return False
            if self.curr_mode != "movie":
                self.set_mode("movie")
        elif isinstance(movie_or_id, str) and fps is None:
            if self.family == "D" or self.version < (2, 5, 6):
                return False
            else:
                movies = self.get_movies()["movies"]
                matches = [entry["id"] for entry in movies if entry["name"]==movie_or_id]
                if matches:
                    self.set_movies_current(matches[0])
                else:
                    return False
            if self.curr_mode != "movie":
                self.set_mode("movie")
        else:
            assert fps
            self.set_mode("off")
            self.upload_movie(movie_or_id, fps, name, force=True)
            self.set_mode("movie")
        return True

    def upload_movie(self, movie, fps, name, force=False):
        """
        Uploads a new movie with the provided frames-per-second and name.
        Note: if the movie does not fit in the remaining capacity, and force is
        not set to True, the function just returns False, in which case the user
        can try clear_movies first.
        Does not switch to movie mode, use show_movie instead for that.
        The movie is an object suitable created with to_movie or make_func_movie.
        Returns the new movie id, which can be used in calls to show_movie or
        show_playlist.

        :param movie: a file-like object that points to movie
        :param fps: frames per second, or None if a movie id is given
        :param bool force: if remaining capacity is too low, previous movies will be removed
        :param str name: name of uploaded movie
        :rtype: int
        """
        numframes = movie.seek(0, 2) // (self.led_bytes * self.num_leds)
        movielst = self.split_movie(movie)
        if self.family == "D" or self.version < (2, 5, 6):
            for ctr, mov, nled in zip(self.ctrlst, movielst, self.nledslst):
                ctr.set_led_movie_config(1000 // fps, numframes, nled)
                ctr.set_led_movie_full(mov)
            return 0
        else:
            res = self.get_movies()
            capacity = res["available_frames"] - 1
            if numframes > capacity or len(res["movies"]) > 15:
                if force:
                    if self.curr_mode == "movie" or self.curr_mode == "playlist":
                        self.set_mode("effect")
                    self.delete_movies()
                else:
                    return False
            if self.curr_mode == "movie":
                oldid = self.get_movies_current()["id"]
            uid = str(uuid.uuid4())
            for ctr, mov, nled in zip(self.ctrlst, movielst, self.nledslst):
                res = ctr.set_movies_new(
                    name,
                    uid,
                    self.led_profile.lower() + "_raw",
                    nled,
                    numframes,
                    fps,
                )
                ctr.set_movies_full(mov)
            if self.curr_mode == "movie":
                self.set_movies_current(oldid)  # Dont change currently shown movie
            return res["id"]

    def show_rt_frame(self, frame):
        """
        Uploads a frame as the next real time frame, and shows it.
        Switches to rt mode if necessary.
        The frame is either a pattern or a one-frame movie

        :param frame: a pattern or file-like object representing the frame
        """
        if self.is_pattern(frame):
            frame = self.to_movie(frame)
        framelst = self.split_movie(frame)
        if self.curr_mode != "rt" or self.last_rt_time + 50.0 < time.time():
            self.set_mode("rt")
        else:
            self.last_rt_time = time.time()
        for ctr, mov, nled in zip(self.ctrlst, framelst, self.nledslst):
            self.udpclient.destination_host = ctr.host
            if self.family == "D":
                ctr.set_rt_frame_socket(mov, 1, nled)
            elif self.version < (2, 4, 14):
                ctr.set_rt_frame_socket(mov, 2)
            else:
                ctr.set_rt_frame_socket(mov, 3)
        self.udpclient.destination_host = self.host

    #def show_playlist(self, lst_or_id, duration):
    #    for ctr in self.ctrlst:
    #        ctr.show_playlist(list_or_id, duration)

    #def show_color(self, rgb):
    #    for ctr in self.ctrlst:
    #        ctr.show_color(rgb)

    #def set_mode(self, mode):
    #    for ctr in self.ctrlst:
    #        ctr.set_mode(mode)

    def clear_movies(self):
        """
        Removes all uploaded movies and any playlist.
        If the current mode is 'movie' or 'playlist' it switches mode to 'effect'
        """
        if self.curr_mode == "movie" or self.curr_mode == "playlist":
            self.set_mode("effect")
        if self.family == "D" or self.version < (2, 5, 6):
            # No list of movies to remove in this version,
            # but disable movie mode until new movie is uploaded
            for i, ctr in enumerate(self.ctrlst):
                ctr.set_led_movie_config(1000, 0, self.nledslst[i])
        else:
            # The playlist is removed automatically when movies are removed
            for ctr in self.ctrlst:
                ctr.delete_movies()

    def get_led_layout(self):
        res = super(MultiHighControlInterface, self).get_led_layout()
        for ctr in self.ctrlst[1:]:
            tmp = ctr.get_led_layout()
            res["coordinates"].extend(tmp["coordinates"])
        return res


