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


def tupleadd(x, y, mul=1):
    return (x[0]+mul*y[0], x[1]+mul*y[1])


class ColorControl:
    def __init__(self, ctr, efflst):
        self.width = 800
        self.height = 800
        self.ctr = ctr
        self.running = False
        self.rtmode = False
        self.outermode = False
        self.win = WindowMgr("Color Control", self.width, self.height, 1, 1)
        rect = (0.2, 0.2, 0.6, 0.6)
        self.sphere = ColorSphere(
            self.win.fig, rect, self.width, self.height, self.win.pixpt, self.on_sphere_click, True
        )
        self.title = CCText(self.win.fig, (0.5, 0.93), "Color Control", 1.0/18)
        self.effect_list = []
        self.sample_list = []
        self.sample_ind = 0
        self.sample_dim = (0.1, 0.1)
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
        for (name,cls) in efflst:
            self.add_effect(cls, name)
        self.add_button((0.4, 0.03, 0.2, 0.1), "Apply", self.apply)
        self.add_glyph((0.07, 0.87, 0.06, 0.06), [(0, 0, 0), (1, 1, 1), (0, 0, 1), (1, 1, 0)], False, self.clear_samples)
        self.add_glyph((0.9, 0.9, 0.06, 0.06), [(0,0.22,0.72),(2,0.22,0.88),(2,0.36,0.96),(2,0.5,1.04),(2,0.64,0.96),(2,0.78,0.88),(2,0.78,0.72),(2,0.78,0.56),(2,0.64,0.48),(2,0.5,0.4),(2,0.5,0.20),(0,0.5,0.0),(1,0.5,0.08)], self.show_help, self.hide_help, True)

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
        ss = min(self.width, self.height) * 0.1
        self.sample_dim = (ss/self.width, ss/self.height)
        self.reposition_samples()
        
    def sample_rect(self, ind, slen, inp=False):
        xmid = 0.1
        ymax = 0.85
        ymin = 0.1
        x0 = xmid - self.sample_dim[0]/2
        y0 = ymax - self.sample_dim[1]
        dy = min(self.sample_dim[1], (ymax - ymin - self.sample_dim[1])/max(1, slen - 1))
        if inp and ind < self.sample_ind:
            return (x0, y0 - (ind+1)*dy + self.sample_dim[1], self.sample_dim[0], dy)
        elif inp and ind > self.sample_ind:
            return (x0, y0 - ind*dy, self.sample_dim[0], dy)
        else:
            return (x0, y0 - ind*dy, self.sample_dim[0], self.sample_dim[1])
        
    def add_sample_last(self):
        ind = len(self.sample_list)
        rect = (0,0,1,1) # Dummy rect - reposition_samples will correct it
        button_funcs = (self.on_sample_press,
                        self.on_sample_motion,
                        self.on_sample_release)
        key_dict = {"delete": self.on_sample_delete,
                    "backspace": self.on_sample_delete}
        sample = CCSample(self.win.fig, rect, self.bg,
                          self.on_sample_select, self.sphere.hsl_color,
                          button_funcs, key_dict)
        self.sample_list.append(sample)
        sample.select()
        self.win.register_target(rect, sample)
        self.reposition_samples()

    def set_sample_color(self, hsl, ev=None):
        self.hsl = hsl
        self.sample_list[self.sample_ind].set_color(hsl, ev)
        if hsl and self.ctr and not self.running:
            if not self.rtmode:
                self.outermode = self.ctr.get_mode()['mode']
                self.rtmode = True
            pat = self.ctr.make_solid_pattern(hsl_color(*hsl))
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
        else:
            self.add_sample_last()
        
    def clear_samples(self):
        for sample in self.sample_list:
            sample.remove()
            self.win.unregister_target(sample)
        self.sample_list = []
        self.sample_ind = 0
        self.add_sample_last()

    def on_sample_select(self, sample):
        ind = self.sample_list.index(sample)
        if int != self.sample_ind:
            self.sample_list[self.sample_ind].unselect()
            self.sample_ind = ind
            self.reposition_samples()
            self.reorder_samples()

    def on_sample_delete(self, event, sample):
        if self.sample_list[self.sample_ind] == sample:
            self.remove_sample(sample)

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
            self.sample_ind = self.dragpos['ind']
            self.dragpos = False
            self.reposition_samples()

    def effect_rect(self, ind):
        return (0.85, 0.75 - ind*0.10, 0.1, 0.1)

    def add_effect(self, cls, lab):
        ind = len(self.effect_list)
        rect = self.effect_rect(ind)
        eff = CCEffect(self.win.fig, rect, self.bg, lab,
                       self.on_effect_press, self.on_effect_unpress,
                       cls)
        self.effect_list.append(eff)
        self.win.register_target(rect, eff)

    def on_effect_press(self, eff, data):
        cls = data
        if self.running:
            self.running.stop_rt()
            self.running = False
        elif not self.rtmode and self.ctr:
            self.outermode = self.ctr.get_mode()['mode']
        for eff0 in self.effect_list:
            if eff0.pressed:
                eff0.pressed = False
                eff0.redraw()
        hlst = self.get_hsl_list()
        if hlst and self.ctr:
            effect = cls(self.ctr, hlst)
            if effect:
                effect.launch_rt()
                self.running = effect
        if self.running:
            eff.pressed = True
            eff.redraw()
        else:
            if self.outermode:
                self.ctr.set_mode(self.outermode)

    def on_effect_unpress(self, eff, data):
        if self.running:
            self.running.stop_rt()
            self.running = False
            if self.outermode:
                self.ctr.set_mode(self.outermode)

    def add_button(self, rect, label, func):
        but = CCButton(self.win.fig, rect, self.bg, label, func)
        self.thing_list.append(but)
        self.win.register_target(rect, but)

    def add_glyph(self, rect, descr, func1, func2, toggle=False):
        gl = CCGlyph(self.win.fig, rect, descr, func1, func2, toggle)
        self.thing_list.append(gl)
        self.win.register_target(rect, gl)

    def get_hsl_list(self):
        return [sample.hsl for sample in self.sample_list if sample.hsl is not None]

    def on_sphere_click(self, hsl, ev):
        if hsl:
            es = self.find_empty_sample()
            if es:
                es.select()
            else:
                self.add_sample_last()
                
    def apply(self):
        if self.running:
            self.running.launch_movie()
            for eff in self.effect_list:
                if eff.pressed:
                    eff.pressed = False
                    eff.redraw()
            self.running = False
            self.outermode = False

    def stop_effects(self, *args):
        if self.running:
            self.running.stop_rt()
        if (self.rtmode or self.running) and self.outermode:
            self.ctr.set_mode(self.outermode)
        self.running = False
        self.rtmode = False

    def show_help(self):
        if not self.help_text:
            txt = 'Rotate the 3D color sphere by dragging its surface\n'\
                  'To get "inside", to less saturated colors, use the scroll wheel.\n\n'\
                  'Create a color scheme to the left by clicking colors on the sphere.\n'\
                  'The color scheme can be reset by clicking the small cross. Samples\n'\
                  'can be rearranged by dragging them, or modified after selecting them.\n\n'\
                  'Then select a dynamic effect to the right. Pre-view it on the leds.\n\n'\
                  'If you are happy with it, upload it as a movie by clicking Apply.\n\n'\
                  'Now, click the questionmark again to get rid of this text.'
            self.help_text = CCText(self.win.fig, (0.5, 0.5), txt, 1.0/48)
        else:
            self.help_text.show()

    def hide_help(self):
        if self.help_text:
            self.help_text.hide()

    def start_event_loop(self):
        self.win.start_event_loop()
