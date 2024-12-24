"""
xled_plus.colorcontrol
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Author: Anders Holst (anders.holst@ri.se), 2024

Graphical user interface for creating, previewing and uploading
dynamic color effects to your led lights.

This code specifies the layout of the interface and its functionality. 
Use instead "xled_plus.xled_colorcontrol" to launch it.

"""

from colorsphere.colorsphere import ColorSphere
from colorsphere.colorwidgets import gray, CCText, CCSample, CCEffect, CCButton, CCGlyph
from colorsphere.windowmgr import WindowMgr
from xled_plus.ledcolor import hsl_color

from tkinter import filedialog
import sys
import os
import re


def tupleadd(x, y, mul=1):
    return (x[0]+mul*y[0], x[1]+mul*y[1])


class ColorControl:
    def __init__(self, ctrlst, effdict):
        self.widthfactor = 1.0 + 0.1 * max(0, (len(effdict)-1)//7)
        self.heightfactor = 1.0 + 0.08 * max(0, (len(ctrlst)-1)//3)
        self.width = 820 * self.widthfactor
        self.height = 820 * self.heightfactor
        self.ctr = ctrlst[0] if ctrlst else None
        self.running = False
        self.rtmode = False
        self.outermode = False
        self.win = WindowMgr("Color Control", self.width, self.height, 1, 1)
        rect = self.normrect((0.2, 0.2, 0.6, 0.6))
        self.sphere = ColorSphere(
            self.win.fig, rect, self.width, self.height, self.win.pixpt, self.on_sphere_click, True
        )
        self.title = CCText(self.win.fig,
                            (0.5, (self.heightfactor - 0.07)/self.heightfactor),
                            "Color Control", 1.0/18/self.heightfactor)
        self.device_list = ctrlst
        self.effect_list = []
        self.sample_list = []
        self.sample_ind = 0
        self.sample_dim = (0.1, 0.1)
        self.button_list = []
        self.thing_list = []
        self.help_text = False
        self.dragpos = False
        self.bg = gray(0.5)
        self.win.set_background(self.bg)
        self.win.register_target(rect, self.sphere)
        self.win.add_motion_callback(self.sphere.color_change_event)
        self.win.add_resize_callback(self.resize)
        self.win.add_close_callback(self.stop_effects)
        self.sphere.mouse_color_callbacks.append(self.set_sample_color)
        self.add_sample_last()
        for i,ctr in enumerate(self.device_list):
            but = self.add_toggle_button(self.device_rect(i),
                                         ctr.get_device_name()['name'],
                                         self.switch_device, self.unset_device, ctr)
            if i==0:
                but.pressed = True
                but.redraw()
        elen = len(effdict)
        for name in effdict:
            (cls, mincol, mindim) = effdict[name]
            self.add_effect(cls, name, elen, (mincol, mindim))
        self.add_cond_button(self.normrect((0.04, 0.03, 0.2, 0.1)), "Load",
                               self.load, self.load_condition)
        self.add_cond_button(self.normrect((0.28, 0.03, 0.2, 0.1)), "Save",
                               self.save, self.save_condition)
        self.add_cond_button(self.normrect((0.52, 0.03, 0.2, 0.1)), "Apply",
                               self.apply, self.apply_condition)
        self.add_cond_button(self.normrect((0.76, 0.03, 0.2, 0.1)), "On/Off",
                               self.toggle_on_off, self.onoff_condition)
        self.add_glyph(self.normrect((0.07, -0.13, 0.06, 0.06)),
                       [(0, 0, 0), (1, 1, 1), (0, 0, 1), (1, 1, 0)],
                       False, self.clear_samples)
        self.add_glyph(self.normrect((-0.1, -0.1, 0.06, 0.06)),
                       [(0,0.22,0.72), (2,0.22,0.88), (2,0.36,0.96),
                        (2,0.5,1.04), (2,0.64,0.96), (2,0.78,0.88),
                        (2,0.78,0.72), (2,0.78,0.56), (2,0.64,0.48),
                        (2,0.5,0.4), (2,0.5,0.20), (0,0.5,0.0), (1,0.5,0.08)],
                       self.show_help, self.hide_help, True)
        for eff in self.effect_list:
            eff.update_cond()
        for but in self.button_list:
            but.update_cond()

    def normrect(self, rect):
        wf = self.widthfactor
        hf = self.heightfactor
        return (rect[0]/wf if rect[0]>=0 else (wf+rect[0])/wf,
                rect[1]/hf if rect[1]>=0 else (hf+rect[1])/hf,
                rect[2]/wf, rect[3]/hf)

    def resize(self, ev):
        self.sphere.resize(ev.width, ev.height)
        self.width = ev.width
        self.height = ev.height
        self.title.resize()
        if self.help_text:
            self.help_text.resize()
        for eff in self.effect_list:
            eff.resize()
        for thing in self.thing_list:
            thing.resize()
        ss = min(self.width/self.widthfactor, self.height/self.heightfactor) * 0.1
        self.sample_dim = (ss/self.width, ss/self.height)
        self.reposition_samples()

    def device_rect(self, ind):
        row = ind // 3
        col = ind % 3
        return self.normrect((0.2+0.2*col, -0.18-0.08*row, 0.19, 0.07))

    def switch_device(self, ctr):
        if self.ctr != ctr:
            eff = self.get_current_effect()
            self.stop_effects()
            self.ctr = ctr
            if eff:
                self.on_effect_press(eff.data)
            for but in self.button_list:
                but.update_cond()

    def unset_device(self, ctr):
        if self.ctr != None:
            self.stop_effects()
            self.ctr = None
            for but in self.button_list:
                but.update_cond()

    def sample_rect(self, ind, slen, inp=False):
        xmid = 0.1/self.widthfactor
        ymax = (self.heightfactor - 0.15)/self.heightfactor
        ymin = 0.15/self.heightfactor
        x0 = xmid - self.sample_dim[0]/2
        y0 = ymax - self.sample_dim[1]
        dy = min(self.sample_dim[1], (ymax - ymin - self.sample_dim[1])/max(1, slen - 1))
        if inp and ind < self.sample_ind:
            return (x0, y0 - (ind+1)*dy + self.sample_dim[1], self.sample_dim[0], dy)
        elif inp and ind > self.sample_ind:
            return (x0, y0 - ind*dy, self.sample_dim[0], dy)
        else:
            return (x0, y0 - ind*dy, self.sample_dim[0], self.sample_dim[1])

    def add_sample_at(self, ind):
        rect = (0,0,1,1) # Dummy rect - reposition_samples will correct it
        button_funcs = (self.on_sample_press,
                        self.on_sample_motion,
                        self.on_sample_release)
        key_dict = {"delete": self.on_sample_delete,
                    "backspace": self.on_sample_delete,
                    "+": self.on_sample_copy}
        sample = CCSample(self.win.fig, rect, self.bg,
                          self.on_sample_select, self.sphere.hsl_color,
                          button_funcs, key_dict)
        if ind >= len(self.sample_list):
            self.sample_list.append(sample)
        else:
            self.sample_list = self.sample_list[0:ind] + [sample] + self.sample_list[ind:]
        self.win.register_target(rect, sample)
        self.reposition_samples()
        return sample

    def add_sample_last(self):
        sample = self.add_sample_at(len(self.sample_list))
        sample.select()
        self.update_colorscheme()

    def set_sample_color(self, hsl, ev=None):
        sample = self.sample_list[self.sample_ind]
        sample.set_color(hsl, ev)
        if sample.hsl and self.ctr and not self.running:
            if not self.rtmode:
                self.outermode = self.ctr.get_mode()['mode']
                self.rtmode = True
            pat = self.ctr.make_solid_pattern(hsl_color(*sample.hsl))
            self.ctr.show_rt_frame(self.ctr.to_movie(pat))
        else:
            if self.rtmode:
                if self.outermode:
                    self.ctr.set_mode(self.outermode)
                self.rtmode = False

    def reposition_samples(self):
        slen = len(self.sample_list)
        for i,sample in enumerate(self.sample_list):
            sample.ax.set_position(self.sample_rect(i, slen))
            self.win.update_target(self.sample_rect(i, slen, inp=True), sample)

    def reorder_samples(self):
        slen = len(self.sample_list)
        for i,sample in enumerate(self.sample_list):
            if i<self.sample_ind:
                sample.ax.set_zorder(i)
            elif i>self.sample_ind:
                sample.ax.set_zorder(slen-1-i)
            else:
                sample.ax.set_zorder(slen)

    def find_empty_sample(self):
        for sample in self.sample_list:
            if sample.hsl is None:
                return sample
        return None

    def remove_sample(self, sample):
        sample.remove()
        self.win.unregister_target(sample)
        self.sample_list.remove(sample)
        es = self.find_empty_sample()
        if es:
            es.select()
            self.reposition_samples()
            self.update_colorscheme()
        else:
            self.add_sample_last()

    def clear_samples(self, *args):
        for sample in self.sample_list:
            sample.remove()
            self.win.unregister_target(sample)
        self.sample_list = []
        self.sample_ind = 0
        self.add_sample_last()

    def on_sample_select(self, sample):
        ind = self.sample_list.index(sample)
        if ind != self.sample_ind:
            self.sample_list[self.sample_ind].unselect()
            self.sample_ind = ind
            self.reposition_samples()
            self.reorder_samples()
            if sample.hsl: # If selecting colored sample, show color
                self.set_sample_color(sample.hsl)

    def on_sample_delete(self, event, sample):
        if self.sample_list[self.sample_ind] == sample:
            self.remove_sample(sample)
            self.set_sample_color(False) # Stop showing color

    def on_sample_copy(self, event, sample):
        if self.sample_list[self.sample_ind] == sample:
            self.add_sample_at(self.sample_ind+1)
            samp = self.sample_list[self.sample_ind+1]
            samp.set_color(sample.hsl)
            self.update_colorscheme()

    def coordtorect(self, x, y):
        return (x/self.width, y/self.height)

    def movelimit(self, pos):
        return (self.dragpos['xpos'], min(max(self.dragpos['range']), max(min(self.dragpos['range']), pos[1])))

    def on_sample_press(self, event, sample):
        sample.select()
        slen = len(self.sample_list)
        pos = self.sample_rect(self.sample_ind, slen)
        r1 = self.sample_rect(0, slen)
        r2 = self.sample_rect(slen-1, slen)
        self.dragpos = {'startrect': pos,
                        'goalrect': pos,
                        'eventpos': self.coordtorect(event.x, event.y),
                        'xpos': r1[0],
                        'range': (r1[1], r2[1]),
                        'ind': self.sample_ind,
                        'len': max(1, slen-1) }

    def on_sample_motion(self, event, sample):
        if self.dragpos is not False:
            evpos = self.coordtorect(event.x, event.y)
            rect = self.dragpos['startrect']
            pos = self.movelimit(tupleadd(tupleadd(evpos, self.dragpos['eventpos'], -1), rect))
            sample.ax.set_position((pos[0], pos[1], rect[2], rect[3]))
            prop = (pos[1] - self.dragpos['range'][0]) / (self.dragpos['range'][1] - self.dragpos['range'][0]) * self.dragpos['len']
            #  swop samle_list, set_position, reorder, update goalrect and ind
            if abs(prop - self.dragpos['ind']) > 0.75:
                i1 = self.dragpos['ind']
                if prop - self.dragpos['ind'] < -0.75:
                    i2 = i1 - 1
                else:
                    i2 = i1 + 1
                sample2 = self.sample_list[i2]
                slen = len(self.sample_list)
                self.sample_list[i1] = sample2
                self.sample_list[i2] = sample
                self.dragpos['ind'] = i2
                self.dragpos['goalrect'] = self.sample_rect(i2, slen)
                sample2.ax.set_position(self.sample_rect(i1, slen))
                if i1<i2:
                    sample2.ax.set_zorder(i1)
                else:
                    sample2.ax.set_zorder(slen-1-i1)

    def on_sample_release(self, event, sample):
        if self.dragpos is not False:
            if self.dragpos['eventpos'] != self.coordtorect(event.x, event.y):
                sample.ax.set_position(self.dragpos['goalrect'])
            if self.sample_ind != self.dragpos['ind']:
                self.sample_ind = self.dragpos['ind']
                self.reposition_samples()
                self.update_colorscheme()
            self.dragpos = False

    def effect_rect(self, ind, elen):
        ncols = (elen-1)//7 + 1
        nrows = (elen-1)//ncols + 1
        col = ind // nrows
        row = ind % nrows
        return self.normrect((-0.05-(ncols-col)*0.1, -0.25-row*0.10, 0.1, 0.1))

    def add_effect(self, cls, lab, elen, cond):
        ind = len(self.effect_list)
        rect = self.effect_rect(ind, elen)
        eff = CCEffect(self.win.fig, rect, self.bg, lab, True,
                       self.on_effect_press, self.on_effect_unpress,
                       data=False, condition_func=self.effect_condition)
        eff.data = (eff, cls, cond)
        self.effect_list.append(eff)
        self.win.register_target(rect, eff)

    def effect_condition(self, data):
        mincol, mindim = data[2]
        return len(self.get_hsl_list()) >= mincol

    def preview_effect(self, cls):
        hlst = self.get_hsl_list()
        if hlst and self.ctr:
            effect = cls(self.ctr, hlst)
            if effect:
                if not (self.rtmode or self.running) and not self.outermode:
                    self.outermode = self.ctr.get_mode()['mode']
                effect.launch_rt()
                self.running = effect
                return True
        return False

    def get_current_effect(self):
        for eff in self.effect_list:
            if eff.pressed:
                return eff
        return False

    def on_effect_press(self, data):
        eff, cls, cond = data
        for eff0 in self.effect_list:
            if eff0.pressed and eff0 is not eff:
                eff0.unpress()
        if self.ctr and not self.preview_effect(cls):
            eff.unpress()
            self.stop_effects()
        for but in self.button_list:
            but.update_cond()

    def on_effect_unpress(self, data):
        self.stop_effects()
        for but in self.button_list:
            but.update_cond()

    def add_cond_button(self, rect, label, func, condfunc=None):
        but = CCButton(self.win.fig, rect, self.bg, label, False, lambda x: func(), False, condition_func=condfunc)
        self.button_list.append(but)
        self.thing_list.append(but)
        self.win.register_target(rect, but)
        return but

    def add_toggle_button(self, rect, label, func1, func2, data):
        but = CCButton(self.win.fig, rect, self.bg, label, True, func1, func2, data)
        self.thing_list.append(but)
        self.win.register_target(rect, but)
        return but

    def add_glyph(self, rect, descr, func1, func2, toggle=False):
        gl = CCGlyph(self.win.fig, rect, descr, toggle, func1, func2)
        self.thing_list.append(gl)
        self.win.register_target(rect, gl)

    def get_hsl_list(self):
        return [sample.hsl for sample in self.sample_list if sample.hsl is not None]

    def on_sphere_click(self, hsl, ev):
        if hsl:
            es = self.find_empty_sample()
            if es:
                es.select()
                self.update_colorscheme()
            else:
                self.add_sample_last()
            self.set_sample_color(hsl)

    def apply(self, data=None):
        eff = self.get_current_effect()
        if eff and self.running:
            self.running.launch_movie()
            self.running = False
            self.outermode = False
            eff.unpress()

    def internal_load(self, f):
        i = 0
        name = False
        efftag = False
        colors = False
        ln = f.readline()
        while ln and i < 10 and not (name and efftag and colors):
            if not (ln == "" or ln == "\n" or ln[0] == "#"):
                i += 1
                if not name:
                    m = re.match("name = \"(.*)\"\n", ln)
                    if m:
                        name = m.group(1)
                if not efftag:
                    m = re.match("effect = \"(.*)\"\n", ln)
                    if m:
                        efftag = m.group(1)
                if not colors:
                    m = re.match("colors = (.*)\n", ln)
                    if m:
                        try:
                            colors = eval(m.group(1))
                        except BaseException:
                            print("internal_load: Failed to interpret color list")
                            colors = False
            ln = f.readline()
        if name and efftag and colors:
            return {"name": name, "effect": efftag, "colors": colors}
        else:
            return False

    def load(self, data=None):
        file = filedialog.askopenfilename()
        if file:
            f = open(file, "r")
            dic = self.internal_load(f)
            f.close()
            if dic:
                self.stop_effects()
                self.clear_samples()
                for i,col in enumerate(dic["colors"]):
                    sample = self.add_sample_at(i)
                    sample.set_color(col)
                self.sample_ind = len(self.sample_list)-1
                for eff in self.effect_list:
                    eff.update_cond()
                    if eff.label == dic["effect"]:
                        eff.pressed = True
                        eff.redraw()
                        self.on_effect_press(eff.data)
                for but in self.button_list:
                    but.update_cond()

    def internal_save(self, f, name, efftag, effcls, cols):
        f.write("#!" + sys.executable + "\n")
        f.write("\n")
        f.write("# This file was generated by colorcontrol.py in the xled_plus package.\n")
        f.write("# Running this code will upload the created effect to your leds.\n")
        f.write("\n")
        f.write("from xled_plus.samples.sample_setup import *\n")
        f.write("\n")
        f.write("name = \"" + name + "\"\n")
        f.write("effect = \"" + efftag + "\"\n")
        f.write("colors = " + str(cols) + "\n")
        f.write("\n")
        f.write("ctr = setup_control()\n")
        estr = str(effcls).split(" ")[-1].split(".")[-1].strip("<>'")
        f.write(estr + "(ctr, colors, name=name).launch_movie()\n")

    def save(self, data=None):
        eff = self.get_current_effect()
        cols = self.get_hsl_list()
        if eff:
            file = filedialog.asksaveasfilename()
            if file:
                f = open(file, "w")
                name = self.running.effect_name if self.running else eff.label
                self.internal_save(f, name, eff.label, eff.data[1], cols)
                try:
                    mode = os.fstat(f.fileno()).st_mode
                    os.fchmod(f.fileno(), mode | 0o111)
                except BaseException:
                    print("save: Failed to change file mode bits")
                    None
                f.close()

    def toggle_on_off(self, data=None):
        if self.rtmode or self.running:
            self.stop_effects()
            self.ctr.turn_off()
        else:
            if self.ctr:
                if self.ctr.is_on():
                    self.ctr.turn_off()
                else:
                    self.ctr.turn_on()
                    eff = self.get_current_effect()
                    if eff:
                        self.on_effect_press(eff.data)

    def stop_effects(self, *args):
        if self.running:
            self.running.stop_rt()
        if (self.rtmode or self.running) and self.outermode:
            self.ctr.set_mode(self.outermode)
            self.outermode = False
        self.running = False
        self.rtmode = False

    def load_condition(self, data):
        return True

    def save_condition(self, data):
        eff = self.get_current_effect()
        return eff and eff.active

    def apply_condition(self, data):
        eff = self.get_current_effect()
        return self.ctr and eff and eff.active

    def onoff_condition(self, data):
        return True if self.ctr else False

    def update_colorscheme(self):
        for eff in self.effect_list:
            eff.update_cond()
        if self.running:
            eff = self.get_current_effect()
            if eff:
                if eff.active:
                    self.on_effect_press(eff.data)
                else:
                    self.on_effect_unpress(eff.data)
                    eff.unpress()
            else:
                self.stop_effects()
                for but in self.button_list:
                    but.update_cond()

    def show_help(self, *args):
        if not self.help_text:
            txt = 'Select one LED device at the top, if you have several.\n\n'\
                  'You can rotate the 3D color sphere by dragging its surface.\n'\
                  'To get "inside", to less saturated colors, use the scroll wheel.\n\n'\
                  'Create a color scheme to the left by clicking colors on the sphere.\n'\
                  'The color scheme can be reset by clicking the small cross. Samples\n'\
                  'can be reordered by dragging them, or modified after selecting them.\n\n'\
                  'Then select a dynamic effect to the right. Pre-view it on the leds.\n\n'\
                  'If you are happy with it, upload it as a movie by clicking Apply.\n\n'\
                  'You can also save the effect to file, and load it back later,\n'\
                  'or the file can be called as a program to upload the effect.\n\n'\
                  'Now, click the questionmark again to get rid of this text.'
            self.help_text = CCText(self.win.fig, (0.5/self.widthfactor, 0.5/self.heightfactor), txt, 1.0/48/self.heightfactor)
        else:
            self.help_text.show()

    def hide_help(self, *args):
        if self.help_text:
            self.help_text.hide()

    def start_event_loop(self):
        self.win.start_event_loop()

