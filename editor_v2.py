import time
import dearpygui.dearpygui as dpg
import dearpygui.demo
import dearpygui.logger as dpg_logger
import json
from dearpygui.demo import show_demo

# for windows
import pydirectinput
pydirectinput.PAUSE = 0

# for osx
# class pydirectinput:
#     @staticmethod
#     def press(key):
#         keyboard.press_and_release(key)
# import keyboard


import threading

class LoggerWrapper:
    def __init__(self, enabled):
        self.enabled = enabled
        if enabled:
            self.impl = dpg_logger.mvLogger()

    def log(self, m):
        if self.enabled:
            self.impl.log(m)

    def log_debug(self, m):
        if self.enabled:
            self.impl.log_debug(m)

    def log_info(self, m):
        if self.enabled:
            self.impl.log_info(m)

logger = LoggerWrapper(True)



# TODO: Drawn / Loading states for when we are waiting for things to finish drawing (inputs currently handle this, but do we need loading bars or something?)
# TODO: Macros
# TODO: Do this via a menu option to add custom macros
# TODO: Handle issues where after loading the 'mouse button' is still thought to be down
# TODO: Probably to handle the issues require 'down' to be in a valid square before continuing the motion
# TODO: Autosave in case of crashes

# TODO: For performance, move 'sending inputs' for the playback out to a separate thread/handler? (I guess they already are but the feedback loop is still too gui tied)


class Constants:
    vp_width = 1000
    vp_height = 800

    slots_per_measure = 16
    measures_count = 3

    notes = [
        {'label': 'C2', 'key': '8'},
        {'label': 'B', 'key': '7'},
        {'label': 'A', 'key': '6'},
        {'label': 'G', 'key': '5'},
        {'label': 'F', 'key': '4'},
        {'label': 'E', 'key': '3'},
        {'label': 'D', 'key': '2'},
        {'label': 'C1', 'key': '1'},
    ]

    special_chars = [
        {'val': 17, 'key': 'Ctrl'},
        {'val': 18, 'key': 'Alt'},
        {'val': 16, 'key': 'Shift'},
        {'val': 9, 'key': 'Tab'},
        {'val': 91, 'key': 'Winkey'},
        {'val': 219, 'key': '['},
        {'val': 221, 'key': ']'},
        {'val': 186, 'key': ';'},
        {'val': 222, 'key': '\''},
        {'val': 188, 'key': ','},
        {'val': 190, 'key': '.'},
        {'val': 191, 'key': '/'},
        {'val': 220, 'key': '\\'},
        {'val': 189, 'key': '-'},
        {'val': 187, 'key': '='},
        {'val': 8, 'key': 'Backspace'},
        {'val': 192, 'key': '`'},
        {'val': 37, 'key': 'Left Arrow'},
        {'val': 40, 'key': 'Down Arrow'},
        {'val': 39, 'key': 'Right Arrow'},
        {'val': 38, 'key': 'Up Arrow'},
        {'val': 32, 'key': 'Space'},
        {'val': 20, 'key': 'Caps Lock'},
        {'val': 13, 'key': 'Enter'},
    ]

class Preferences:
    def __init__(self):
        self.macros = [
            {'macro': 'Play / Stop', 'val': None, 'param': None, 'param_enabled': False},
            {'macro': 'Load File 1', 'val': None, 'param': '<file>', 'param_enabled': True},
        ]

    def save(self):
        out = open('prefs.json', mode='w')
        out.write(json.dumps(self.macros))

    def load(self):
        input = open('prefs.json', mode='r')
        in_str = input.read()
        if len(in_str) > 0:
            obj = json.loads(in_str)
            self.macros = obj


class UIMacro:

    # Purpose is to update the 'val' property of preference with whatever is input on the 'dialog'
    def update_param(self, sender, data):
        print('update_param data={d}'.format(d=data))
        dpg.set_item_user_data(sender, data)

    def save_param(self, new_param):
        self.preference['param'] = new_param
        self.close_input(False)

    def show_param_input(self):
        px = (Constants.vp_width - 200) / 2
        py = (Constants.vp_height - 100) / 2

        with dpg.window(popup=True, modal=True, label='Param Input', width=200, height=100, pos=[px, py],
                        no_close=True, no_resize=False, no_move=False) as w:
            Elements.dpg_button_input_window = w

            t = dpg.add_input_text(default_value=self.preference['param'], pos=[20, 100 / 2 - 10], callback=self.update_param)
            dpg.add_button(label="OK", width=50, pos=[20, 100 - 30], callback=lambda: self.save_param(dpg.get_item_user_data(t)))
            dpg.add_button(label="Cancel", width=50, pos=[200 - 20 - 50, 100 - 30],
                           callback=lambda: self.save_param(self.preference['param']))










    # Purpose is to update the 'val' property of preference with whatever is input on the 'dialog'
    def update_keys(self, new_keys, data, text):
        key = data[0]
        if key not in new_keys:
            new_keys.append(key)

        s = ''
        for iter, k in enumerate(new_keys):
            if iter > 0:
                s += '+'
            s += Elements.key_to_str(k)

        dpg.configure_item(text, default_value=s)

    def save_keys(self, new_keys):
        self.preference['val'] = new_keys

        self.close_input(True)

    def show_key_input(self):
        kdl = None
        px = (Constants.vp_width - 200) / 2
        py = (Constants.vp_height - 100) / 2

        new_keys = []

        with dpg.window(popup=True, modal=True, label='Key Input', width=200, height=100, pos=[px, py], no_close=True, no_resize=True, no_move=True, on_close=lambda: {
            # Clean up the listener on close
            dpg.delete_item(kdl)
        }) as w:
            Elements.dpg_button_input_window = w

            t = dpg.add_text(default_value='<>', pos=[20, 100 / 2 - 10])
            dpg.add_button(label="OK", width=50, pos=[20, 100 - 30], callback=lambda: self.save_keys(new_keys))
            dpg.add_button(label="Cancel", width=50, pos=[200 - 20 - 50, 100 - 30], callback=lambda: self.save_keys(self.preference['val']))

            with dpg.handler_registry(id="bi_registry"):
                kdl = dpg.add_key_down_handler(callback=lambda s, d: self.update_keys(new_keys, d, t))

    def close_input(self, do_delete_registry):
        logger.log_debug('close_key_input trace')

        if Elements.dpg_button_input_window is not None:
            dpg.delete_item(Elements.dpg_button_input_window)
            Elements.dpg_button_input_window = None

        if do_delete_registry:
            dpg.delete_item(item="bi_registry")

        Elements.prefs.save()
        Elements.show_macros()


    # action -> lambda to call on macro usage (i.e. when it is activated)
    def __init__(self, action, preference):
        self.action = action
        self.preference = preference

        key_str = ''
        if self.preference['val'] is not None:
            for iter, v in enumerate(self.preference['val']):
                if iter > 0:
                    key_str += '+'
                key_str += Elements.key_to_str(v)
        else:
            key_str = '< >'
        self.key = key_str

    def draw(self, parent):
        dpg.add_text(parent=parent, default_value=self.preference['macro'])
        dpg.add_table_next_column(parent=parent)

        dpg.add_button(parent=parent, label=self.key, callback=self.show_key_input)
        dpg.add_table_next_column(parent=parent)

        dpg.add_button(parent=parent, label=self.preference['param'], callback=self.show_param_input, show=self.preference['param_enabled'])
        dpg.add_table_next_column(parent=parent)

class Elements:
    dpg_window = None
    dpg_macros_window = None
    dpg_button_input_window = None
    dpg_macro_table = None
    dpg_add_macro_button = None
    prefs = Preferences()

    @staticmethod
    def add_file_macro():
        f_macro_num = len(Elements.prefs.macros)
        new_m = {
            'macro': 'Load File {n}'.format(n=f_macro_num), 'val': [], 'param': '<file>', 'param_enabled': True
        }
        Elements.prefs.macros.append(new_m)
        Elements.refresh_macros()

    @staticmethod
    def refresh_macros():
        if Elements.dpg_macro_table is not None:
            dpg.delete_item(Elements.dpg_macro_table)
        if Elements.dpg_add_macro_button is not None:
            dpg.delete_item(Elements.dpg_add_macro_button)

        Elements.dpg_macro_table = dpg.add_table(parent=Elements.dpg_macros_window, header_row=True)
        dpg.add_table_column(parent=Elements.dpg_macro_table, label='Action')
        dpg.add_table_column(parent=Elements.dpg_macro_table, label='Key')
        dpg.add_table_column(parent=Elements.dpg_macro_table, label='Param')

        for m in Elements.prefs.macros:
            ui_mac = UIMacro(lambda: print('macro action'), m)
            ui_mac.draw(Elements.dpg_macro_table)

        Elements.dpg_add_macro_button = dpg.add_button(parent=Elements.dpg_macros_window, label="Add File Macro", callback=Elements.add_file_macro)


    @staticmethod
    def show_macros():
        MouseStats.handlers_enabled = False

        if Elements.dpg_macros_window is None:
            h = 400
            w = 400
            logger.log_debug('showing macros window: {w}'.format(w=w))
            px = (Constants.vp_width - w) / 2
            py = (Constants.vp_height - h) / 2
            Elements.dpg_macros_window = dpg.add_window(label='Configure Macros', width=w, height=400, pos=[px, py], modal=True, popup=True, on_close=lambda: Elements.hide_macros())

            Elements.prefs.load()

            # -------------
            # |  [ play / stop ] [ <key> ]
            # |  [ load_file   ] [ <key> ] [ <file> ]
            # |  <button to add more load_file macros>

            Elements.refresh_macros()


    @staticmethod
    def hide_macros():
        if Elements.dpg_macros_window is not None:
            Elements.prefs.save()

            dpg.delete_item(Elements.dpg_macro_table)
            Elements.dpg_macro_table = None

            dpg.delete_item(Elements.dpg_add_macro_button)
            Elements.dpg_add_macro_button = None

            dpg.delete_item(Elements.dpg_macros_window)
            Elements.dpg_macros_window = None

        MouseStats.handlers_enabled = True

    @staticmethod
    def key_to_str(key):
        entry = None
        for sk in Constants.special_chars:
            if sk['val'] == key:
                entry = sk
                break
        if entry is None:
            return chr(key)
        else:
            return entry['key']

    @staticmethod
    def update_macro_pref(d, text, new_keys):
        if d[0] not in new_keys:
            new_keys.append(d[0])

        t_str = ''
        for iter, d in enumerate(new_keys):
            if iter > 0:
                t_str += '+'
            t_str += Elements.key_to_str(d)
        dpg.configure_item(text, default_value=t_str)


# Data classes
# Measure
# Octave
# Note
# Slot


#       M
# -----------------
#       O   N  S S S S S S S S S S S S S S S S
#           N  S S S S S S S S S S S S S S S S
#           N  S S S S S S S S S S S S S S S S
#           N  S S S S S S S S S S S S S S S S
#           N  S S S S S S S S S S S S S S S S
#           N  S S S S S S S S S S S S S S S S
#           N  S S S S S S S S S S S S S S S S
#           N  S S S S S S S S S S S S S S S S
# -----------------
#       O   N  S S S S S S S S S S S S S S S S
#           N  S S S S S S S S S S S S S S S S
#           N  S S S S S S S S S S S S S S S S
#           N  S S S S S S S S S S S S S S S S
#           N  S S S S S S S S S S S S S S S S
#           N  S S S S S S S S S S S S S S S S
#           N  S S S S S S S S S S S S S S S S
#           N  S S S S S S S S S S S S S S S S
# -----------------
#       O   N  S S S S S S S S S S S S S S S S
#           N  S S S S S S S S S S S S S S S S
#           N  S S S S S S S S S S S S S S S S
#           N  S S S S S S S S S S S S S S S S
#           N  S S S S S S S S S S S S S S S S
#           N  S S S S S S S S S S S S S S S S
#           N  S S S S S S S S S S S S S S S S
#           N  S S S S S S S S S S S S S S S S

# TODO: Perhaps make restriction on how notes work across octaves (i.e. no multiple notes at the same time across multiple octaves)


class Slot:

    def __init__(self):
        self.activated = False
        self.is_held_note = False
        self.playing = False
        self.drawn = False
        self.change_triggered = False
        self.rect = None
        self.rect_text = None
        self.note_key = None
        self.note_octave = None

    def assign_note_key(self, nk, no):
        self.note_key = nk
        self.note_octave = no

    def set_rect(self, r):
        self.rect = r

    def set_rect_text(self, r):
        self.rect_text = r

    def change(self, type):
        if self.change_triggered:
            return

        # type -> 0 add, 1 remove, 2 tertiary add (held notes -- don't actually activate)
        # also, if already activated then toggle with held or not
        if self.activated and type == 0:
            self.is_held_note = True
            self.activated = False
        elif self.is_held_note and type == 0:
            self.activated = True
            self.is_held_note = False
        else:
            self.activated = (type == 0)
            self.change_triggered = True
            self.is_held_note = (type == 2)

        dpg.configure_item(self.rect, fill=self.fill())
        dpg.configure_item(self.rect_text, show=(self.activated or self.is_held_note))

    def clear(self):
        self.activated = False
        self.change_triggered = False
        self.playing = False

        dpg.configure_item(self.rect, fill=self.fill())
        dpg.configure_item(self.rect_text, show=(self.activated or self.is_held_note))
        dpg.configure_item(self.rect, color=self.color())


    def clear_change_trigger(self):
        self.change_triggered = False

    def send_inputs(self):
        pydirectinput.press(self.note_key['key'])

    def play(self):
        self.playing = True
        dpg.configure_item(self.rect, color=self.color())

        if self.activated:
            self.send_inputs()

    def finished(self):
        self.playing = False
        dpg.configure_item(self.rect, color=self.color())


    def fill(self):
        if self.is_held_note:
            return [0, 255, 255, 255]
        elif self.activated:
            return [0, 255, 0, 255]
        else:
            return [255, 255, 255, 255]

    def color(self):
        return [0, 0, 255, 255] if self.playing else [255, 255, 255, 255]


class Note:

    def __init__(self, note, octave):
        self.note = note
        self.octave = octave
        self.slots = []
        for i in range(Constants.slots_per_measure):
            s = Slot()
            s.assign_note_key(self.note, self.octave)
            self.slots.append(s)


class Octave:

    def __init__(self, octave_val):
        self.octave_val = octave_val
        self.notes = []
        for i in range(len(Constants.notes)):
            note = Constants.notes[i]
            new_note = Note(note, self.octave_val)
            self.notes.append(new_note)


class Measure:

    def __init__(self):
        self.octaves = [
            Octave(2),  # high
            Octave(1),  # default
            Octave(0)   # low
        ]


# View classes
class ControlBar:

    def __init__(self):
        self.control_bar = None
        self.play_pause = None
        self.clear_but = None
        self.save = None
        self.load = None
        self.measure_cnt_ctrl = None
        self.measure_cnt_ctrl_apply = None
        self.bpm_ctrl = None
        self.bpm_ctrl_apply = None

        self.macros_menu_btn = None

    def refresh(self):
        if self.control_bar is None:
            return

        dpg.configure_item(self.play_pause, label="Play")
        dpg.configure_item(self.measure_cnt_ctrl, default_value=Constants.measures_count)
        dpg.configure_item(self.bpm_ctrl, default_value=TimeManager.BPM)

    def clear(self):
        if self.control_bar is not None:
            dpg.delete_item(self.control_bar)
            self.control_bar = None

    def width(self):
        return dpg.get_viewport_width()

    def height(self):
        return 50

    def cb_play(self, sender, app_data):
        logger.log("cb_play trace")

        toggled = dpg.get_item_user_data(self.play_pause)
        toggled = not toggled
        dpg.set_item_user_data(self.play_pause, toggled)

        l = "Play" if not toggled else "Stop"
        dpg.set_item_label(self.play_pause, label=l)

        if toggled:
            start_timer()
        else:
            stop_timer()

    def cb_cnt_changed(self, sender, app_data):
        dpg.set_item_user_data(sender, app_data)

    # TODO: Just add measures / remove from current list, don't re-init
    def cb_apply(self, sender, app_data):
        cnt = dpg.get_item_user_data(self.measure_cnt_ctrl)
        Constants.measures_count = cnt
        main_window.refresh({})

    def cb_save(self, sender, app_data):
        logger.log("cb_save trace")
        MouseStats.handlers_enabled = False
        ControlBar.file_select_purpose = 'save'
        dpg.show_item("song_sel")

    def cb_load(self, sender, app_data):
        logger.log("cb_load trace")
        MouseStats.handlers_enabled = False
        ControlBar.file_select_purpose = 'load'
        dpg.show_item("song_sel")

    def cb_bpm_changed(self, sender, app_data):
        dpg.set_item_user_data(sender, app_data)

    def cb_apply_bpm(self, sender, app_data):
        bpm = dpg.get_item_user_data(self.bpm_ctrl)
        TimeManager.BPM = bpm

        global g_tm
        if g_tm is not None and g_tm.alive:
            g_tm.kill()

    def cb_clear(self, sender, app_data):
        dpg.set_item_user_data(self.play_pause, False)
        dpg.set_item_label(self.play_pause, label="Play")

        stop_timer()
        main_window.refresh({})

    file_select_purpose = 'load'
    def cb_file_select(self, sender, app_data):
        logger.log("cb_file_select trace, app_data: {s}".format(s=app_data))
        MouseStats.handlers_enabled = True
        if ControlBar.file_select_purpose == 'load':
            load(app_data['file_path_name'])
        elif ControlBar.file_select_purpose == 'save':
            save(app_data['file_path_name'])

    def cb_macros_btn(self, sender, app_data):
        logger.log("cb_macros_btn trace")
        Elements.show_macros()


    def draw(self):
        self.clear()

        with dpg.child(parent=Elements.dpg_window, pos=[0, 0], autosize_x=True, autosize_y=True) as c:
            self.control_bar = c
            self.play_pause = dpg.add_button(label="Play", callback=self.cb_play, pos=[0, 0], height=self.height(), width=50)
            dpg.set_item_user_data(self.play_pause, False)

            self.clear_but = dpg.add_button(label="Clear", callback=self.cb_clear, pos=[60, 0], height=self.height(), width=50)

            self.save = dpg.add_button(label="Save", callback=self.cb_save, pos=[120, 0], height=self.height(), width=50)
            self.load = dpg.add_button(label="Load", callback=self.cb_load, pos=[180, 0], height=self.height(), width=50)

            self.measure_cnt_ctrl = dpg.add_input_int(label="# of Measures", callback=self.cb_cnt_changed, pos=[260, 20], default_value=Constants.measures_count, width=100)
            self.measure_cnt_ctrl_apply = dpg.add_button(label="Apply", callback=self.cb_apply, pos=[470, 0], height=self.height(), width=50)
            dpg.set_item_user_data(self.measure_cnt_ctrl, Constants.measures_count)

            self.bpm_ctrl = dpg.add_input_int(label="BPM", callback=self.cb_bpm_changed, pos=[540, 20], default_value=TimeManager.BPM, max_value=999, width=100)
            self.bpm_ctrl_apply = dpg.add_button(label="Apply", callback=self.cb_apply_bpm, pos=[680, 0], height=self.height(), width=50)
            dpg.set_item_user_data(self.bpm_ctrl, TimeManager.BPM)

            # Button to open the macros window
            self.macros_menu_btn = dpg.add_button(label="Macros", callback=self.cb_macros_btn, pos=[750, self.height() / 2], height=self.height() / 2)


class InfoBar:
    def __init__(self):
        self.data_label = 'Debug_Info: '
        self.mouse_pos = []
        self.translated_mouse_pos = []
        self.data_text = None
        self.play_index = 0

    def refresh(self):
        dpg.configure_item(self.data_text, default_value=self.data_string())

    def set_mouse_pos(self, mouse_pos):
        self.mouse_pos = mouse_pos
        self.refresh()

    def set_translated_mouse_pos(self, mouse_pos):
        self.translated_mouse_pos = mouse_pos
        self.refresh()

    def set_play_index(self, index):
            self.play_index = index
            self.refresh()

    def data_string(self):
        return "{label} mouse_pos: {mp} translated: {mp2} play_index: {pi}".format(
            label=self.data_label,
            mp=self.mouse_pos,
            mp2=self.translated_mouse_pos,
            pi=self.play_index,
        )

    def draw(self):
        global main_window
        self.data_text = dpg.add_text(parent=Elements.dpg_window, pos=[10, 65], default_value=self.data_string())


class MeasuresDisplay:
    drawlist_offset = 30
    def __init__(self):
        self.measures_panel = None
        self.drawlist_panel = None
        self.measures = []
        self.measure_displays = []

    def refresh(self):
        # clear our drawn items
        # Can't delete all children, note_labels are children
        # need to only delete our drawn stuff
        # dpg.delete_item(self.measures_panel, children_only=True)
        for md in self.measure_displays:
            md.clear()
        self.measure_displays.clear()
        dpg.delete_item(self.drawlist_panel)
        self.drawlist_panel = None
        self.draw_slots()

    def set_data(self, d):
        self.measures = d

    def clear(self):
        if self.measures_panel is not None:
            dpg.delete_item(self.measures_panel)
            self.measures_panel = None

    def content_width(self):
        # oct_width = num slots * slot width
        # full width = num measures * oct width
        oct_w = len(self.measures[0].octaves[0].notes[0].slots) * MeasureDisplay.slot_width
        return len(self.measures) * (oct_w + MeasureDisplay.measure_spacing)

    def content_height(self):
        # oct_height = num notes * note slot height
        # measure height = num octaves * oct height
        oct_h = len(self.measures[0].octaves[0].notes) * MeasureDisplay.slot_height
        return len(self.measures[0].octaves) * (oct_h + MeasureDisplay.octave_spacing)

    def draw_slots(self):
        with dpg.drawlist(parent=self.measures_panel, pos=[MeasuresDisplay.drawlist_offset, 0], width=self.content_width(),
                          height=self.content_height() + 50) as dl:
            self.drawlist_panel = dl
            for iteration, m in enumerate(self.measures):
                md = MeasureDisplay()
                md.set_data(m, iteration)
                self.measure_displays.append(md)

                md.draw(dl)

    def draw(self):
        # self.clear()

        with dpg.child(parent=Elements.dpg_window, horizontal_scrollbar=True, autosize_y=True, autosize_x=True, pos=[0, 100]) as p:
            self.measures_panel = p
            self.draw_slots()


class MeasureDisplay:
    slot_width = 30
    slot_height = 20
    slot_spacing = 4

    octave_spacing = 40
    measure_spacing = 10

    def __init__(self):
        self.measure = None
        self.measure_panel = None
        self.octave_panels = []
        self.measure_dl = None
        self.index = 0
        self.items = []

    def clear(self):
        for i in self.items:
            dpg.delete_item(i)
        self.items.clear()

    def set_data(self, d, i):
        self.measure = d
        self.index = i

    def measure_width(self):
        # width of measure is # of slots * slot width
        return len(self.measure.octaves[0].notes[0].slots) * MeasureDisplay.slot_width

    def measure_height(self):
        # height of measure is # of notes * slot_height
        return len(self.measure.octaves[0].notes) * MeasureDisplay.slot_height

    def draw_octave(self, parent, measure_ind, octave_ind):
        oct = self.measure.octaves[octave_ind]

        # measure_ind == x offset
        # octave_ind == y offset
        x_off = measure_ind * (self.measure_width() + MeasureDisplay.measure_spacing)
        y_off = octave_ind * (self.measure_height() + MeasureDisplay.octave_spacing)

        bar_pos = [x_off, y_off + self.measure_height()]
        measure_indicator_bar = dpg.draw_rectangle(pmin=bar_pos, pmax=[bar_pos[0] + self.measure_width(), bar_pos[1] + 20], fill=[75, 75, 75, 255])
        measure_indicator_text = dpg.draw_text(pos=[bar_pos[0] + (self.measure_width() / 2) - 40, bar_pos[1] + 2], size=14, text='Measure #{n}'.format(n=measure_ind), color=[255, 255, 255, 255])

        # for each octave, draw the associated rectangles for the notes / slots
        for note_iter, note in enumerate(oct.notes):
            for slot_iter, slot in enumerate(note.slots):

                draw_quarter_bar = (slot_iter % 4) == 0

                start_x = x_off + slot_iter * MeasureDisplay.slot_width
                start_y = y_off + note_iter * MeasureDisplay.slot_height
                r = dpg.draw_rectangle(
                    pmin=[start_x + (MeasureDisplay.slot_spacing / 2), start_y + (MeasureDisplay.slot_spacing / 2)],
                    pmax=[start_x + MeasureDisplay.slot_width - (MeasureDisplay.slot_spacing / 2),
                          start_y + MeasureDisplay.slot_height - (MeasureDisplay.slot_spacing / 2)],
                    fill=slot.fill(),
                    color=slot.color(),
                    thickness=4,
                )
                t = 'o{ov}{nk}'.format(ov=slot.note_octave, nk=slot.note_key['label'])
                rect_text = dpg.draw_text(size=11, show=(slot.activated or slot.is_held_note), color=[0, 0, 0, 255], text=t, pos=[start_x + (MeasureDisplay.slot_spacing / 2) + 1, start_y + (MeasureDisplay.slot_spacing / 2) + 2])
                slot.set_rect(r)
                slot.set_rect_text(rect_text)

                if draw_quarter_bar:
                    sx = start_x + (MeasureDisplay.slot_spacing / 2)
                    sy = start_y + (MeasureDisplay.slot_spacing / 2)
                    ex = sx
                    ey = start_y + MeasureDisplay.slot_height - (MeasureDisplay.slot_spacing / 2)
                    dpg.draw_line(p1=[sx, sy], p2=[ex, ey], thickness=1, color=[255, 0, 0, 255])

    def delegate_mouse_down(self, pos, type):
        global main_window

        # Things to care about when determining what rect we are in:
        # 'window' position (top-left corner) on the screen: dpg.get_viewport_pos()
        # scroll offset of the measures display child

        # self.index is the index of the measure we are
        slot_found = None
        for oct_ind, oct in enumerate(self.measure.octaves):
            if slot_found is not None:
                break

            x_off = self.index * (self.measure_width() + MeasureDisplay.measure_spacing) + MeasuresDisplay.drawlist_offset
            y_off = oct_ind * (self.measure_height() + MeasureDisplay.octave_spacing)

            for note_iter, note in enumerate(oct.notes):
                if slot_found is not None:
                    break
                for slot_iter, slot in enumerate(note.slots):

                    start_x = x_off + slot_iter * MeasureDisplay.slot_width
                    start_y = y_off + note_iter * MeasureDisplay.slot_height

                    in_x = start_x <= pos[0] <= start_x + MeasureDisplay.slot_width
                    in_y = start_y <= pos[1] <= start_y + MeasureDisplay.slot_height

                    if in_x and in_y:
                        slot_found = slot
                        break

        if slot_found is not None:
            slot_found.change(type)
            return True

        return False

    def draw(self, parent):
        # draw 3 octaves
        self.draw_octave(parent, self.index, 2)
        self.draw_octave(parent, self.index, 1)
        self.draw_octave(parent, self.index, 0)


class NoteLabels:

    def draw(self):
        h = dpg.get_item_height(Elements.dpg_window)
        with dpg.drawlist(parent=main_window.measures.measures_panel, height=h, width=50, pos=[10, 0]) as dl:
            for i in range(3):
                # per octave
                for nl_iter, nl in enumerate(Constants.notes):

                    y_off = i * (MeasureDisplay.octave_spacing + (MeasureDisplay.slot_height * len(Constants.notes))) + (nl_iter * MeasureDisplay.slot_height)

                    dpg.draw_text(size=12, text=nl['label'], pos=[0, y_off])


class MainWindow:

    def __init__(self):
        self.controls = None
        self.info = None
        self.measures = None
        self.note_labels = None

        self.controls = ControlBar()
        self.info = InfoBar()
        self.measures = MeasuresDisplay()
        init_measures(Constants.measures_count)
        self.measures.set_data(g_measures)
        self.note_labels = NoteLabels()

    def clear(self):
        dpg.delete_item(Elements.dpg_window, children_only=True)
        MouseStats.handlers_enabled = False

    def refresh(self, opts):
        global g_measures

        MouseStats.handlers_enabled = False

        self.controls.refresh()
        self.info.refresh()

        # TODO: Potential problem here as g_measures is mutable -- probably need to do some refactoring to keep it safe
        if 'measures' in opts:
            g_measures = opts['measures']
        else:
            init_measures(Constants.measures_count)
        self.measures.set_data(g_measures)
        self.measures.refresh()

        MouseStats.handlers_enabled = True

    def draw(self):
        MouseStats.handlers_enabled = False

        self.controls.draw()
        self.info.draw()
        self.measures.draw()
        self.note_labels.draw()

        MouseStats.handlers_enabled = True


def on_viewport_resize():
    logger.log_debug('viewport resized: {w}x{h}'.format(w=dpg.get_viewport_width(), h=dpg.get_viewport_height()))
    Constants.vp_width = dpg.get_viewport_width()
    Constants.vp_height = dpg.get_viewport_height()


def render_callback():
    x = 1
    # Not important, currently as the timer was moved out of this render loop


g_measures = []
g_slots = []
def init_measures(count):
    global g_measures
    global g_slots
    g_measures.clear()
    for i in range(count):
        g_measures.append(Measure())

    # make a list of slots for access elsewhere (like clearing)
    g_slots.clear()
    for m in g_measures:
        for o in m.octaves:
            for n in o.notes:
                for s in n.slots:
                    g_slots.append(s)

def save(fname):
    global g_measures

    # 130[o0n1-o0n5-o1n3-o2n4]
    # BPM[<--> note info]
    #    [octave+note-octave+note-etc]

    f = open(fname, 'w')
    f.write(str(TimeManager.BPM))

    # TODO: Test case for [] meaning empty slots for that index
    for m in g_measures:

        for slot_index in range(len(m.octaves[0].notes[0].slots)):
            f.write('[')
            write_delim = False
            for o in m.octaves:
                for n in o.notes:
                    slot = n.slots[slot_index]

                    if slot.activated or slot.is_held_note:
                        if write_delim:
                            f.write('-')

                        f.write('o{ov}{nt}{nv}'.format(ov=slot.note_octave, nt='n' if slot.activated else 'h', nv=slot.note_key['key']))
                        write_delim = True

            f.write(']')


# TODO: Save / load needs to work with held notes as well
def load(fname):
    global g_measures
    global main_window

    logger.log_info('loading file: {f}'.format(f=fname))

    stop_timer()

    f = open(fname, 'r')
    song_info = f.read()

    # n can be n or h (n is activated, h is held note)
    # 130[o0n1-o0n5-o1n3-o2n4]
    # BPM[<--> note info]
    #    [octave+note-octave+note-etc]

    # parse the info
    first_index = song_info.index('[')
    bpm = song_info[0:first_index]
    notes = song_info[first_index:]

    logger.log_debug('load, bpm: {b}'.format(b=bpm))
    logger.log_debug('load, notes: {n}'.format(n=notes))

    parsed_measures = [Measure()]
    measure_index = 0
    slot_index = 0

    while len(notes) > 0:
        logger.log_debug('load, len: {l}'.format(l=len(notes)))

        range_begin = notes.index('[')
        range_end = notes.index(']')
        range = notes[range_begin+1:range_end]

        logger.log_debug('parse info: {rb} {re} {r}'.format(rb=range_begin, re=range_end, r=range))

        # do something with the info
        if slot_index >= Constants.slots_per_measure:
            measure_index += 1
            slot_index = 0
            parsed_measures.append(Measure())
            logger.log_debug('new measure')

        if range_end == (range_begin + 1):
            notes = notes[range_end + 1:]
            logger.log_debug('new notes: {n}'.format(n=notes))

            slot_index += 1
            continue

        # TODO: Sanitization of parsed values instead of just crashing for bad indices
        octave_notes = range.split('-')
        for on in octave_notes:
            # first 2 chars are the octave indicator
            oct_ind = on[0:2]
            # second 2 chars are the note indicator
            note_ind = on[2:4]

            logger.log_debug('oct_ind: {oi}, note_ind: {ni}'.format(oi=oct_ind, ni=note_ind))

            note_type = note_ind[0]

            oct_val = int(oct_ind[1])
            note_val = note_ind[1]

            logger.log_debug('oct_val: {ov}, note_val: {nv}'.format(ov=oct_val, nv=note_val))
            logger.log_debug('parsed_measures: ' + str(parsed_measures))

            selected_oct = None
            for o in parsed_measures[measure_index].octaves:
                if o.octave_val == oct_val:
                    selected_oct = o
                    break
            if selected_oct is not None:
                for n in selected_oct.notes:
                    if n.note['key'] == note_val:
                        if note_type == 'h':
                            n.slots[slot_index].is_held_note = True
                        elif note_type == 'n':
                            n.slots[slot_index].activated = True
                        break

        notes = notes[range_end+1:]
        logger.log_debug('new notes: {n}'.format(n=notes))

        slot_index += 1

    # after building our parsed measures, replace our g_measures and draw
    Constants.measures_count = len(parsed_measures)
    TimeManager.BPM = int(bpm)

    main_window.refresh({'measures': parsed_measures})
    print_measures()


# Not sure if I am fully on board with the mouse temp disable stuff, but it is preventing errors with dialogs / notes for now (i.e. not accidentally writing notes when not meaning to)
class MouseStats:
    is_down = False
    is_down_secondary = False
    is_down_tertiary = False
    is_temp_disabled = False
    pos = None

    handlers_enabled = False

    def moved(self, sender, app_data):
        global g_measures
        global main_window

        if not MouseStats.handlers_enabled or MouseStats.is_temp_disabled:
            logger.log_debug('moved disabled')
            return False

        self.pos = app_data

        translated_mouse_pos = [
            self.pos[0] + dpg.get_x_scroll(main_window.measures.measures_panel),
            self.pos[1] + dpg.get_y_scroll(main_window.measures.measures_panel) - dpg.get_item_pos(main_window.measures.measures_panel)[1],
        ]

        main_window.info.set_mouse_pos(self.pos)
        main_window.info.set_translated_mouse_pos(translated_mouse_pos)

        type = 0 if self.is_down else 1 if self.is_down_secondary else 2 if self.is_down_tertiary else -1
        if self.is_down or self.is_down_secondary or self.is_down_tertiary:
            found = False
            for mdisplay in main_window.measures.measure_displays:
                found = mdisplay.delegate_mouse_down(translated_mouse_pos, type)
                if found:
                    logger.log_debug('found, ret true')
                    return True
            if not found:
                MouseStats.is_temp_disabled = True


        logger.log_debug('not found, ret false')
        return False



    def downed(self, sender, app_data):
        if not MouseStats.handlers_enabled:
            return
        if self.is_down or self.is_down_secondary or self.is_down_tertiary:
            return

        # primary
        primary_down = dpg.is_mouse_button_down(0)

        # secondary
        secondary_down = dpg.is_mouse_button_down(1)

        # tertiary
        tertiary_down = dpg.is_mouse_button_down(2)

        logger.log_debug('downed')
        if primary_down:
            self.is_down = True
        elif secondary_down:
            self.is_down_secondary = True
        elif tertiary_down:
            self.is_down_tertiary = True

        detected = self.moved(sender, self.pos)
        if not detected:
            MouseStats.is_temp_disabled = True
            logger.log_debug('temp_disabled true')

    def upped(self):
        MouseStats.is_temp_disabled = False
        logger.log_debug('temp_disabled false')

        if not MouseStats.handlers_enabled:
            return
        if not self.is_down and not self.is_down_secondary and not self.is_down_tertiary:
            return

        logger.log_debug('upped')
        self.is_down = False
        self.is_down_secondary = False
        self.is_down_tertiary = False

        # reset trigger states for all slots
        for m in g_measures:
            for o in m.octaves:
                for n in o.notes:
                    for s in n.slots:
                        s.clear_change_trigger()


ms = MouseStats()
def setup_global_handlers():
    global ms
    dpg.add_mouse_move_handler(callback=ms.moved, user_data=dpg.get_mouse_pos())
    dpg.add_mouse_down_handler(callback=ms.downed, user_data=dpg.get_mouse_pos())
    dpg.add_mouse_release_handler(callback=ms.upped, user_data=dpg.get_mouse_pos())


main_window = None
def start_editor():
    global main_window

    # init_measures(3)

    Elements.dpg_window = dpg.add_window(id='MIDI_Editor', width=Constants.vp_width, height=Constants.vp_height)
    dpg.setup_viewport()
    with dpg.handler_registry():
        setup_global_handlers()
    dpg.set_viewport_resize_callback(callback=on_viewport_resize)

    if main_window is None:
        main_window = MainWindow()
        main_window.draw()

    fd = dpg.add_file_dialog(modal=True, show=False, callback=main_window.controls.cb_file_select, id="song_sel")
    dpg.add_file_extension(extension=".gwm", parent=fd)

    dpg.set_viewport_width(Constants.vp_width)
    dpg.set_viewport_height(Constants.vp_height)
    dpg.set_primary_window("MIDI_Editor", True)
    # dpg.set_viewport_resizable(False)
    # dpg.show_style_editor()

    while dpg.is_dearpygui_running():
        render_callback()
        dpg.render_dearpygui_frame()

    dpg.cleanup_dearpygui()


class TimeManager(threading.Thread):
    BPM = 120

    # 60k / BPM = quarter
    # 60k * 4 / BPM = full
    # 60k * 1/2 / BPM = eighth
    # 60k * 1/4 / BPM = sixteenth
    mult = 4 / Constants.slots_per_measure

    def __init__(self):
        self.tick_cb = None
        self.finished_cb = None
        self.mult = 4 / Constants.slots_per_measure

        if Constants.slots_per_measure == 4:
            self.speed = (60 * self.mult) / TimeManager.BPM
        if Constants.slots_per_measure == 8:
            self.speed = (60 * self.mult) / TimeManager.BPM
        if Constants.slots_per_measure == 16:
            self.speed = (60 * self.mult) / TimeManager.BPM

        self.alive = True
        threading.Thread.__init__(self)

    def set_cb(self, tick_cb, finished_cb):
        self.tick_cb = tick_cb
        self.finished_cb = finished_cb

    def run(self):
        time.sleep(1)   # initial play delay
        while self.alive:
            time.sleep(self.speed)
            self.tick()

        if self.finished_cb is not None:
            self.finished_cb()

    def tick(self):
        logger.log_debug('TimeManager tick')
        if self.alive and self.tick_cb is not None:
            self.tick_cb()

    def kill(self):
        self.alive = False


play_time = -1
last_tick_slots = []
last_octave = 1
def time_tick():
    global last_tick_slots
    global last_octave
    global play_time
    global g_measures
    global g_tm

    for s in last_tick_slots:
        s.finished()
    last_tick_slots.clear()

    play_time += 1
    # treat this as an 'index' to the slot to use in playback in measures


    if play_time >= len(g_measures) * Constants.slots_per_measure:
        # finished
        g_tm.kill()
        return

    # num of slots per measure is the mod to determine which measure the slot is in
    measure_index = int(play_time / Constants.slots_per_measure)
    m = g_measures[measure_index]

    o0 = m.octaves[0]
    o1 = m.octaves[1]
    o2 = m.octaves[2]

    # slot index in the notes is the remainder
    slot_index = play_time % Constants.slots_per_measure

    main_window.info.set_play_index('play_time: {pt} measure_index: {mi} slot_index: {si}'.format(pt=play_time, mi=measure_index, si=slot_index))

    # TODO: When playing notes, only 'switch' octave as necessary (i.e. we detect that the next note is on a different octave, don't switch back until we need to)

    # determine which octave has notes to play
    prev_last_octave = last_octave
    oct_found = None
    for o in m.octaves:
        if oct_found:
            break
        for n in o.notes:
            s = n.slots[slot_index]
            if s.activated:
                last_octave = o.octave_val
                oct_found = o
                break

    # default if not found
    if oct_found is None:
        # last_octave = 1
        oct_found = m.octaves[1]

    logger.log_debug('last_octave: {lo}   prev_last_octave: {plo}'.format(lo=last_octave, plo=prev_last_octave))

    # 'switch' octaves as necessary
    if last_octave > prev_last_octave:
        for i in range(last_octave - prev_last_octave):
            pydirectinput.press('0')  # move up
            time.sleep(0.01)
    elif last_octave < prev_last_octave:
        for i in range(prev_last_octave - last_octave):
            pydirectinput.press('9')  # move down
            time.sleep(0.01)

    # 'play' them all
    for n in oct_found.notes:
        s = n.slots[slot_index]
        s.play()
        last_tick_slots.append(s)

    # assign our scroll
    scroll_width = (main_window.measures.measure_displays[0].measure_width() * measure_index) + (slot_index * MeasureDisplay.slot_width)
    logger.log_debug('scroll_width: ' + str(scroll_width) + '   mi: ' + str(measure_index) + '   si: ' + str(slot_index))
    dpg.set_x_scroll(main_window.measures.measures_panel, scroll_width)


def time_finished():
    global last_tick_slots

    dpg.set_item_user_data(main_window.controls.play_pause, False)
    dpg.set_item_label(main_window.controls.play_pause, "Play")
    dpg.set_x_scroll(main_window.measures.measures_panel, 0)

    last_tick_slots.clear()



g_tm = None
def start_timer():
    global g_tm
    global play_time
    global last_octave
    if g_tm is None or not g_tm.alive:
        last_octave = 1
        play_time = -1
        g_tm = TimeManager()
        g_tm.set_cb(time_tick, time_finished)
        g_tm.start()

def stop_timer():
    global g_tm
    global play_time
    global last_tick_slots
    if g_tm is not None:
        g_tm.kill()
        # g_tm.join()
        play_time = -1
    last_tick_slots.clear()


def print_measures():
    for m in g_measures:
        for o in m.octaves:
            logger.log_debug('octave{o}'.format(o=o.octave_val))
            for n in o.notes:
                logger.log_debug('note{n}'.format(n=n.note))
                for s in n.slots:
                    logger.log_debug('slot{s}'.format(s=s.activated))

    logger.log_debug('measures: {m}'.format(m=g_measures))


if __name__ == '__main__':
    # midi_editor.run_editor()
    # dearpygui.demo.show_demo()
    # dpg.start_dearpygui()
    start_editor()
    # keyboard.wait()