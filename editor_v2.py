import time
import dearpygui.dearpygui as dpg
import dearpygui.demo
import dearpygui.logger as dpg_logger
import json
from dearpygui.demo import show_demo
from midi_editor import midi_importer


# for windows
import pydirectinput
pydirectinput.PAUSE = 0

# for osx
# class pydirectinput:
#     @staticmethod
#     def press(key):
#         keyboard.press_and_release(key)
import keyboard


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

logger = LoggerWrapper(False)



# Utility
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


from playsound import playsound
import queue
# For now, only piano
class SampleManager(threading.Thread):

    def __init__(self):
        self.sample_queue = queue.Queue()
        self.alive = True
        threading.Thread.__init__(self)

    def kill(self):
        self.alive = False
        self.sample_queue.put(None)

    def push_sample(self, sample):
        self.sample_queue.put(sample)

    def run(self):
        while self.alive:
            sample = self.sample_queue.get()
            if sample is None:
                self.sample_queue.task_done()
                continue

            if main_window.controls.sounds_enabled():
                threading.Thread(target=play_sample, args=(sample['note'], sample['octave'],), daemon=True).start()
            self.sample_queue.task_done()


sample_manager = SampleManager()
sample_manager.start()
def play_sample(note, octave):
    if note == 'C2':
        if octave == 2:
            playsound('assets/samples/piano/c7.mp3')
        elif octave == 1:
            playsound('assets/samples/piano/c6.mp3')
        elif octave == 0:
            playsound('assets/samples/piano/c5.mp3')
    elif note == 'B':
        if octave == 2:
            playsound('assets/samples/piano/b6.mp3')
        elif octave == 1:
            playsound('assets/samples/piano/b5.mp3')
        elif octave == 0:
            playsound('assets/samples/piano/b4.mp3')
    elif note == 'A':
        if octave == 2:
            playsound('assets/samples/piano/a6.mp3')
        elif octave == 1:
            playsound('assets/samples/piano/a5.mp3')
        elif octave == 0:
            playsound('assets/samples/piano/a4.mp3')
    elif note == 'G':
        if octave == 2:
            playsound('assets/samples/piano/g6.mp3')
        elif octave == 1:
            playsound('assets/samples/piano/g5.mp3')
        elif octave == 0:
            playsound('assets/samples/piano/g4.mp3')
    elif note == 'F':
        if octave == 2:
            playsound('assets/samples/piano/f6.mp3')
        elif octave == 1:
            playsound('assets/samples/piano/f5.mp3')
        elif octave == 0:
            playsound('assets/samples/piano/f4.mp3')
    elif note == 'E':
        if octave == 2:
            playsound('assets/samples/piano/e6.mp3')
        elif octave == 1:
            playsound('assets/samples/piano/e5.mp3')
        elif octave == 0:
            playsound('assets/samples/piano/e4.mp3')
    elif note == 'D':
        if octave == 2:
            playsound('assets/samples/piano/d6.mp3')
        elif octave == 1:
            playsound('assets/samples/piano/d5.mp3')
        elif octave == 0:
            playsound('assets/samples/piano/d4.mp3')
    elif note == 'C1':
        if octave == 2:
            playsound('assets/samples/piano/c6.mp3')
        elif octave == 1:
            playsound('assets/samples/piano/c5.mp3')
        elif octave == 0:
            playsound('assets/samples/piano/c4.mp3')




# TODO: Handle issues where after loading the 'mouse button' is still thought to be down
# TODO: Probably to handle the issues require 'down' to be in a valid square before continuing the motion
# TODO: For performance, move 'sending inputs' for the playback out to a separate thread/handler? (I guess they already are but the feedback loop is still too gui tied)
# TODO: General refactoring
# TODO: Add synchronization stuff01
# TODO: Add .mid format parsing / import (stretch goal)
# TODO: Loading / clearing still occasionally crashes (need to investigate here)
# TODO: Control to 'lock' the song, preventing edits
# TODO: Interpolate note scrolling during playback (linear)

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


def macro_action_play_stop():
    print('macro_action_play_stop')
    main_window.controls.cb_play(0, {})

def macro_action_load_file(param):
    print('macro_action_load_file: {p}'.format(p=param))
    ControlBar.file_select_purpose = 'load'
    main_window.controls.cb_file_select(0, {'file_path_name': param})

assigned_macros = []
def assign_macros():
    # clear / assign macros
    clear_macros()
    for m in Elements.prefs.macros:
        assign_macro(m)

def clear_macros():
    global assigned_macros
    print('clearing macros')

    for m in assigned_macros:
        keyboard.remove_hotkey(m)

    assigned_macros.clear()

def assign_macro(m):
    global assigned_macros

    key_string = ''
    for iter, k in enumerate(m['val']):
        if iter > 0:
            key_string += '+'
        key_string += key_to_str(k).lower()

    action = m['action']
    if action not in Preferences.action_types:
        logger.log_info('Invalid action supplied: {m}'.format(m=m))
    else:
        print('assigning macro: {m}, keys: {k}'.format(m=m, k=key_string))
        if action == 'play_stop':
            handler = keyboard.add_hotkey(key_string, macro_action_play_stop, suppress=True, trigger_on_release=True)
            assigned_macros.append(handler)
        elif action == 'load_file':
            handler = keyboard.add_hotkey(key_string, lambda: macro_action_load_file(m['param']), suppress=True, trigger_on_release=True)
            assigned_macros.append(handler)


class Preferences:
    action_types = [
        'play_stop',
        'load_file'
    ]

    def __init__(self):
        self.macros = [
            {'macro': 'Play / Stop', 'val': None, 'param': None, 'param_enabled': False, 'action': 'play_stop'},
            {'macro': 'Load File 1', 'val': None, 'param': '<file>', 'param_enabled': True, 'action': 'load_file'},
        ]

        self.load()

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
    # Purpose is to update the 'param' property of preference with whatever is input on the 'dialog'
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
            s += key_to_str(k)

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
                key_str += key_to_str(v)
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
    dpg_save_macros_button = None
    prefs = Preferences()

    @staticmethod
    def add_file_macro():
        f_macro_num = len(Elements.prefs.macros)
        new_m = {
            'macro': 'Load File {n}'.format(n=f_macro_num), 'val': [], 'param': '<file>', 'param_enabled': True, 'action': 'load_file'
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
        Elements.dpg_save_macros_button = dpg.add_button(parent=Elements.dpg_macros_window, label="Save Macros", callback=Elements.save_macros)


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

            clear_macros()  # Ensure we don't suppress while assigning macros
            Elements.prefs.load()
            Elements.refresh_macros()

    @staticmethod
    def save_macros():
        Elements.prefs.save()
        assign_macros()
        Elements.hide_macros()

    @staticmethod
    def hide_macros():
        if Elements.dpg_macros_window is not None:
            dpg.delete_item(Elements.dpg_macro_table)
            Elements.dpg_macro_table = None

            dpg.delete_item(Elements.dpg_add_macro_button)
            Elements.dpg_add_macro_button = None

            dpg.delete_item(Elements.dpg_macros_window)
            Elements.dpg_macros_window = None

        MouseStats.handlers_enabled = True

    @staticmethod
    def update_macro_pref(d, text, new_keys):
        if d[0] not in new_keys:
            new_keys.append(d[0])

        t_str = ''
        for iter, d in enumerate(new_keys):
            if iter > 0:
                t_str += '+'
            t_str += key_to_str(d)
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
            self.change_triggered = True
        elif self.is_held_note and type == 0:
            self.activated = True
            self.is_held_note = False
            self.change_triggered = True
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
        sample_manager.push_sample({'note': self.note_key['label'], 'octave': self.note_octave})

    def play(self):
        self.playing = True
        self.item = dpg.configure_item(self.rect, color=self.color())

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
        self.play_sounds = None
        self.import_but = None

        self.macros_menu_btn = None

    def disable(self):
        dpg.configure_item(self.clear_but, enabled=False)
        dpg.configure_item(self.save, enabled=False)
        dpg.configure_item(self.load, enabled=False)
        dpg.configure_item(self.measure_cnt_ctrl, enabled=False)
        dpg.configure_item(self.measure_cnt_ctrl_apply, enabled=False)
        dpg.configure_item(self.bpm_ctrl, enabled=False)
        dpg.configure_item(self.bpm_ctrl_apply, enabled=False)
        dpg.configure_item(self.macros_menu_btn, enabled=False)

    def enable(self):
        dpg.configure_item(self.clear_but, enabled=True)
        dpg.configure_item(self.save, enabled=True)
        dpg.configure_item(self.load, enabled=True)
        dpg.configure_item(self.measure_cnt_ctrl, enabled=True)
        dpg.configure_item(self.measure_cnt_ctrl_apply, enabled=True)
        dpg.configure_item(self.bpm_ctrl, enabled=True)
        dpg.configure_item(self.bpm_ctrl_apply, enabled=True)
        dpg.configure_item(self.macros_menu_btn, enabled=True)

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
        global g_measures
        cnt = dpg.get_item_user_data(self.measure_cnt_ctrl)
        Constants.measures_count = cnt

        new_measures = []
        new_measures.extend(g_measures)

        diff = cnt - len(g_measures)
        print('diff: {d}'.format(d=diff))
        if diff > 0:
            # add more
            for i in range(diff):
                new_measures.append(Measure())
        elif diff < 0:
            # remove from new_measures
            new_measures = new_measures[:diff]  # slice backwards

        print('apply new_measures: {n}'.format(n=new_measures))
        main_window.refresh({'measures': new_measures})

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

    def cb_sounds_check_changed(self, sender, app_data):
        dpg.set_item_user_data(sender, app_data)

    def sounds_enabled(self):
        return dpg.get_item_user_data(self.play_sounds)

    def cb_import(self):
        print('cb_import')
        MouseStats.handlers_enabled = False  # TODO: Need to re-enable elsewhere
        dpg.show_item("import_sel")


    def draw(self):
        self.clear()

        with dpg.child(parent=Elements.dpg_window, pos=[0, 0], autosize_x=True, autosize_y=True) as c:

            self.control_bar = c
            self.play_pause = dpg.add_button(label="Play", callback=self.cb_play, pos=[0, 0], height=self.height() / 2, width=50)
            dpg.set_item_user_data(self.play_pause, False)

            self.clear_but = dpg.add_button(label="Clear", callback=self.cb_clear, pos=[60, 0], height=self.height() / 2, width=50)

            self.save = dpg.add_button(label="Save", callback=self.cb_save, pos=[120, 0], height=self.height() / 2, width=50)
            self.load = dpg.add_button(label="Load", callback=self.cb_load, pos=[180, 0], height=self.height() / 2, width=50)

            self.measure_cnt_ctrl = dpg.add_input_int(label="# of Measures", callback=self.cb_cnt_changed, pos=[260, 3], default_value=Constants.measures_count, width=100)
            self.measure_cnt_ctrl_apply = dpg.add_button(label="Apply", callback=self.cb_apply, pos=[450, 0], height=self.height() / 2, width=50)
            dpg.set_item_user_data(self.measure_cnt_ctrl, Constants.measures_count)

            self.bpm_ctrl = dpg.add_input_int(label="BPM", callback=self.cb_bpm_changed, pos=[540, 3], default_value=TimeManager.BPM, max_value=999, width=100)
            self.bpm_ctrl_apply = dpg.add_button(label="Apply", callback=self.cb_apply_bpm, pos=[670, 0], height=self.height() / 2, width=50)
            dpg.set_item_user_data(self.bpm_ctrl, TimeManager.BPM)

            self.play_sounds = dpg.add_checkbox(label='Play Sounds', default_value=False, pos=[750, 3], callback=self.cb_sounds_check_changed)

            # Button to open the macros window
            self.macros_menu_btn = dpg.add_button(label="Macros", callback=self.cb_macros_btn, pos=[870, 0], height=self.height() / 2)

            self.import_but = dpg.add_button(label='Import', callback=self.cb_import, pos=[950, 0], height=self.height() / 2)

            with dpg.theme(id="controls_bar_theme"):
                dpg.add_theme_color(target=dpg.mvThemeCol_ChildBg, value=[31, 15, 16, 255], category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(target=dpg.mvThemeCol_Button, value=[110, 21, 15, 255], category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(target=dpg.mvThemeCol_ButtonHovered, value=[165, 35, 32, 255], category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(target=dpg.mvThemeCol_ButtonActive, value=[90, 15, 12, 255], category=dpg.mvThemeCat_Core)

            dpg.set_item_theme(item=c, theme="controls_bar_theme")

            # dpg.show_style_editor()


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
            dpg.set_item_font(item=dl, font="note_font")

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
    slot_width = 35
    slot_height = 25
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
        measure_indicator_text = dpg.draw_text(pos=[bar_pos[0] + (self.measure_width() / 2) - 40, bar_pos[1] + 2], size=12, text='Measure #{n}  Octave {o}'.format(n=measure_ind + 1, o=2-octave_ind), color=[255, 255, 255, 255])
        dpg.set_item_font(item=measure_indicator_text, font="gw2_font_def")

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
                t = '{nk}'.format(nk=slot.note_key['label'])
                rect_text = dpg.draw_text(size=10, show=(slot.activated or slot.is_held_note), color=[0, 0, 0, 255], text=t, pos=[start_x + (MeasureDisplay.slot_spacing / 2) + 4, start_y + (MeasureDisplay.slot_spacing / 2) + 2])
                # dpg.set_item_font(item=rect_text, font="note_font")
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
            # auto-save
            save('auto_save.gwm.tmp')
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

class ScrubBar:
    def __init__(self):
        self.sb_dl = None
        self.rect_positions = []


    def draw(self):
        # draw list -> rects in single row that you can select as the 'play' position
        y_off = main_window.measures.content_height()
        print('scrub bar width: {w}'.format(w=main_window.measures.content_width()))

        self.sb_dl = dpg.add_drawlist(parent=main_window.measures.measures_panel, pos=[MeasuresDisplay.drawlist_offset, y_off + 10], width=main_window.measures.content_width(), height=MeasureDisplay.slot_height)
        self.refresh()

    def refresh(self):
        global play_time_start
        print('scrub bar width: {w}'.format(w=main_window.measures.content_width()))
        dpg.configure_item(self.sb_dl, width=main_window.measures.content_width())

        dpg.delete_item(self.sb_dl, children_only=True)
        slots_width_count = len(g_measures) * Constants.slots_per_measure
        for i in range(slots_width_count):
            r_x_off = (i * MeasureDisplay.slot_width) + (MeasureDisplay.measure_spacing * int(i / Constants.slots_per_measure))

            r = {
                "index": i,
                "pmin": [r_x_off + (MeasureDisplay.slot_spacing / 2), 0],
                "pmax": [r_x_off + MeasureDisplay.slot_width - (MeasureDisplay.slot_spacing / 2), MeasureDisplay.slot_height],
            }
            self.rect_positions.append(r)

            fill = [255, 255, 255, 255]
            if i == (play_time_start + 1): # +1 b/c we assign to -1 to hit the proper index on first tick
                fill = [255, 0, 0, 255]
            dpg.draw_rectangle(parent=self.sb_dl, pmin=r['pmin'], pmax=r['pmax'], fill=fill)

    def slot_clicked(self, index):
        global play_time_start
        play_time_start = index - 1 # -1 b/c we want the first 'tick' to hit this index
        self.refresh()

    def delegate_click(self):
        # Determine which slot we've clicked and apply it to the 'play_time' that we use to start the timer at
        print('delegate_click')

        pos = dpg.get_mouse_pos()
        translated_mouse_pos = [
            pos[0] + dpg.get_x_scroll(main_window.measures.measures_panel) - MeasuresDisplay.drawlist_offset,
            pos[1] + dpg.get_y_scroll(main_window.measures.measures_panel) - dpg.get_item_pos(self.sb_dl)[1],
        ]
        print('dg pos: {p}'.format(p=translated_mouse_pos))

        for rect in self.rect_positions:
            pmin = rect['pmin']
            pmax = rect['pmax']
            in_x = pmin[0] <= translated_mouse_pos[0] <= pmax[0]
            in_y = pmin[1] <= translated_mouse_pos[1] <= pmax[1]
            if in_x and in_y:
                # found, use this index in the callback
                self.slot_clicked(rect['index'])
                return True

        return False


class MainWindow:

    def __init__(self):
        self.controls = None
        self.info = None
        self.measures = None
        self.note_labels = None
        self.scrub_bar = None

        self.controls = ControlBar()
        self.info = InfoBar()
        self.measures = MeasuresDisplay()
        init_measures(Constants.measures_count)
        self.measures.set_data(g_measures)
        self.note_labels = NoteLabels()
        self.scrub_bar = ScrubBar()

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

        print('main_window refresh opts: {o}'.format(o=opts))

        self.measures.set_data(g_measures)
        self.measures.refresh()
        self.scrub_bar.refresh()

        MouseStats.handlers_enabled = True

    def draw(self):
        MouseStats.handlers_enabled = False

        self.controls.draw()
        self.info.draw()
        self.measures.draw()
        self.note_labels.draw()
        self.scrub_bar.draw()

        MouseStats.handlers_enabled = True


def on_viewport_resize():
    logger.log_debug('viewport resized: {w}x{h}'.format(w=dpg.get_viewport_width(), h=dpg.get_viewport_height()))
    Constants.vp_width = dpg.get_viewport_width()
    Constants.vp_height = dpg.get_viewport_height()


def render_callback():
    x = 1
    # Not important, currently as the timer was moved out of this render loop


g_measures = []
def init_measures(count):
    global g_measures
    g_measures.clear()
    for i in range(count):
        g_measures.append(Measure())

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

    global play_time_start
    play_time_start = -1
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

        # any_down = dpg.is_mouse_button_down(0) or dpg.is_mouse_button_down(1) or dpg.is_mouse_button_down(2)
        # if not any_down or not app_data:
        #     self.upped()
        #     return False

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


        # logger.log_debug('not found, ret false')
        return False



    def downed(self, sender, app_data):
        if not MouseStats.handlers_enabled or MouseStats.is_temp_disabled:
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

        # first, detect if we are attempting to scrub
        handled = main_window.scrub_bar.delegate_click()
        if handled:
            return

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
def window_closed():
    # do some general cleanup
    # print('window_closed stopping timer...')
    # stop_timer()
    # print('window_closed timer stopped')
    sample_manager.kill()
    print('window_closed sample_manager joining...')
    sample_manager.join()
    print('window_closed sample_manager joined')

def import_selected(sender, app_data):
    print('import_selected: {d}'.format(d=app_data))
    midi_importer.show_importer(app_data['file_path_name'], perform_import, Constants.vp_width, Constants.vp_height)

def note_length_to_ui_slots(note_length):
    # returns [1,0,0,0] as example meaning 4 slots, the first being a strung note and the 3 after being held notes
    if note_length == 'note_1':
        return [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    elif note_length == 'note_2':
        return [1,0,0,0,0,0,0,0]
    elif note_length == 'note_4':
        return [1,0,0,0]
    elif note_length == 'note_8':
        return [1,0]
    elif note_length == 'note_16':
        return [1]
    else:
        return []

def pick_closest_note_key(note_length_key):
    # for now, go 'down'
    # notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    if note_length_key == 'C#':
        return 'C1'
    elif note_length_key == 'D#':
        return 'D'
    elif note_length_key == 'F#':
        return 'F'
    elif note_length_key == 'G#':
        return 'G'
    elif note_length_key == 'A#':
        return 'A'
    else:
        return note_length_key

def map_octaves(channel_notes):
    used_octaves = [
        0,   # 0
        0,   # 1
        0,   # 2
        0,   # 3
        0,   # 4
        0,   # 5
        0,   # 6
        0,   # 7
        0,   # 8
        0,   # 9
    ]

    for note in channel_notes:
        note_positions = channel_notes[note]
        for p in note_positions:
            used_octaves[p['repr']['octave']] = used_octaves[p['repr']['octave']] + 1


    # find sliding window of highest 3 together (store begin / end) and output the subarray as the highest 3
    begin = 0
    end = 2
    cv = None
    for i in range(len(used_octaves) - 2):
        print('2 used_octaves: {u}'.format(u=used_octaves))
        new_total = used_octaves[i] + used_octaves[i + 1] + used_octaves[i + 2]
        print('uo: {u}'.format(u=used_octaves[i]))
        print('val1: {v1}, val2: {v2}, val3: {v3}'.format(v1=used_octaves[begin], v2=used_octaves[begin+1], v3=used_octaves[end]))
        print('i: {i}, new_total: {n}'.format(i=i, n=new_total))
        if cv is None or new_total > cv:
            cv = new_total
            begin = i
            end = i + 2

    return {begin: 0, (begin+1): 1, (begin+2): 2}

def perform_import(data):
    # print('perform_import: {d}'.format(d=data))
    parsed_measures = [Measure()]
    measure_index = 0
    slot_index = 0

    # notes are in order, first filter by channel
    sel_channel = data['selected_channel']
    used_octaves = map_octaves(data['data'])

    for note in data['data']:
        if slot_index >= Constants.slots_per_measure:
            measure_index += 1
            slot_index = 0
            parsed_measures.append(Measure())

        note_positions = data['data'][note]
        # use position to convert to 'cursor'
        # use 'cursor' as index in measures / slots

        # time to index
        # ticks_per_beat * 4 == full measure -> 384 * 4 = 1536
        # full measure / Constants.slots_per_measure == ticks per slot -> 1536 / 16 = 96
        # position (in ticks)               X
        # -------------------  *   ------------------------   = position * #slots / ticks in measure ->  (192 * 16) / 1536 = 2
        #  ticks in measure              # slots in measure

        # beats per measure = 4 (4/4 time)
        measure_ticks = midi_importer.Utility.ticks_per_beat * 4
        ticks_per_slot = measure_ticks / Constants.slots_per_measure

        for p in note_positions:
            total_index = int(p['position'] / ticks_per_slot)
            total_to_add = int(p['length'] / ticks_per_slot)

            measure_index = int(total_index / Constants.slots_per_measure)
            slot_index = int(total_index % Constants.slots_per_measure)

            while measure_index >= len(parsed_measures):
                parsed_measures.append(Measure())

            oct_val = p['repr']['octave']
            note_val = p['repr']['note']

            if oct_val in used_octaves:
                real_oct = used_octaves[oct_val]

                selected_octave = list(filter(lambda octave: octave.octave_val == real_oct, parsed_measures[measure_index].octaves))
                if len(selected_octave) > 0:

                    for n in selected_octave[0].notes:
                        if n.note['label'] == note_val:

                            print('n: {n}'.format(n=n))

                            # for each tick in length, mark a slot as activated or held depending on first or not
                            n.slots[slot_index].activated = True

                            inner_measure_index = measure_index
                            inner_measure = parsed_measures[inner_measure_index]
                            inner_octave = list(filter(lambda octave: octave.octave_val == real_oct,
                                                          inner_measure.octaves))

                            print('total to add: {t}'.format(t=total_to_add))
                            additional_index = slot_index
                            for i in range(1, total_to_add):
                                additional_index += 1
                                if additional_index >= Constants.slots_per_measure:
                                    parsed_measures.append(Measure())

                                    additional_index = 0
                                    inner_measure_index += 1
                                    inner_measure = parsed_measures[inner_measure_index]
                                    inner_octave = list(filter(lambda octave: octave.octave_val == real_oct,
                                                               inner_measure.octaves))

                                print('inner_octave: {io}, inner_measure: {im}, inner_measure_index: {m}, additional_index: {a}, i: {i2}'.format(io=inner_octave, im=inner_measure, m=inner_measure_index, a=additional_index, i2=i))
                                for ion in inner_octave[0].notes:
                                    if ion.note['label'] == note_val:
                                        print('additional_index: {a}'.format(a=additional_index))
                                        ion.slots[additional_index].is_held_note = True
                                        break





    # print('channel_notes len: {l}'.format(l=len(list(channel_notes))))


    # find the 3 most used octaves and build a mapping for the current octave that they are to the allowed octave vals (0, 1, 2)
    #
    # for note in channel_notes:
    #     print('slot_index: {s}, measure_index: {m}'.format(s=slot_index, m=measure_index))
    #
    #     if slot_index >= Constants.slots_per_measure:
    #         measure_index += 1
    #         slot_index = 0
    #         parsed_measures.append(Measure())
    #
    #     # length of note
    #     note_length = note.closest_note_length()['type']
    #     empty_delay_before_note = note.offset_note()  # 'silence' means the 'val' of this note is the 'length' denoted by the 'type' returned in 'val' instead
    #     note_key = note.note_repr['note']
    #     note_octave = note.note_repr['octave']
    #
    #     # Add empty slots first
    #     if empty_delay_before_note['type'] == 'silence':
    #         # skip X slots based on the value
    #         to_skip = note_length_to_ui_slots(empty_delay_before_note['val'])
    #
    #         for i in range(len(to_skip)):
    #             slot_index += 1
    #             if slot_index >= Constants.slots_per_measure:
    #                 measure_index += 1
    #                 slot_index = 0
    #                 parsed_measures.append(Measure())
    #
    #     to_add = note_length_to_ui_slots(note_length)
    #     print('to_add: {t}'.format(t=to_add))
    #
    #     # TODO: Improve this so we don't re-filter each iteration
    #     # TODO: Filter out octaves we can't play, treat them as silence (i.e just skip to the next slot index)
    #     # TODO: The 'octave' values we need to use are the 3 most used octave numbers that are sequential (to get the most notes)
    #     # TODO: The below does not work with chords (it moves the slot index instead of checking for notes that are at the same 'time')
    #     for i in to_add:
    #         real_octave = -1 if note_octave not in used_octaves else used_octaves[note_octave]
    #         print('note_octave: {n1}, note_octave to select: {n}, used_octaves: {uo}'.format(n1=note_octave, n=real_octave, uo=used_octaves))
    #         sel_octave = list(filter(lambda octave: octave.octave_val == real_octave, parsed_measures[measure_index].octaves))
    #
    #         if(len(sel_octave) <= 0):
    #             slot_index += 1
    #             if slot_index >= Constants.slots_per_measure:
    #                 measure_index += 1
    #                 slot_index = 0
    #                 parsed_measures.append(Measure())
    #             continue
    #
    #         for n in sel_octave[0].notes:
    #             if n.note['label'] == note_key:
    #                 if i == 0:
    #                     n.slots[slot_index].is_held_note = True
    #                 elif i == 1:
    #                     n.slots[slot_index].activated = True
    #
    #                 slot_index += 1
    #                 if slot_index >= Constants.slots_per_measure:
    #                     measure_index += 1
    #                     slot_index = 0
    #                     parsed_measures.append(Measure())

    Constants.measures_count = len(parsed_measures)
    TimeManager.BPM = data['bpm']

    global play_time_start
    play_time_start = -1
    main_window.refresh({'measures': parsed_measures})
    print_measures()
    # enable mouse again?


def start_editor():
    global main_window

    # init_measures(3)

    Elements.dpg_window = dpg.add_window(id='MIDI_Editor', width=Constants.vp_width, height=Constants.vp_height, on_close=window_closed)
    dpg.setup_viewport()
    with dpg.handler_registry():
        setup_global_handlers()
    dpg.set_viewport_resize_callback(callback=on_viewport_resize)

    # add a font registry
    with dpg.font_registry():
        dpg.add_font(id='gw2_font_def', file="assets/fonts/GWTwoFont.ttf", size=13, default_font=True)
        dpg.add_font(id='note_font', file="assets/fonts/dogica.otf", size=10, default_font=False)
        dpg.add_font(id='gw2_font', file="assets/fonts/GWTwoFont.ttf", size=80, default_font=False)

    if main_window is None:
        main_window = MainWindow()
        main_window.draw()

        # load any currently assigned macros
        assign_macros()

    ifd = dpg.add_file_dialog(modal=True, show=False, callback=import_selected, id="import_sel", default_path="./assets/midi_test/")
    dpg.add_file_extension(extension=".mid", parent=ifd)

    fd = dpg.add_file_dialog(modal=True, show=False, callback=main_window.controls.cb_file_select, id="song_sel")
    dpg.add_file_extension(extension=".gwm", parent=fd)

    dpg.set_viewport_width(Constants.vp_width)
    dpg.set_viewport_height(Constants.vp_height)
    dpg.set_primary_window("MIDI_Editor", True)
    dpg.set_viewport_title("Gwidi")
    # dpg.set_viewport_resizable(False)
    # dpg.show_style_editor()

    # dpg.show_metrics()
    while dpg.is_dearpygui_running():
        render_callback()
        dpg.render_dearpygui_frame()

    dpg.cleanup_dearpygui()

    print('cleanup occurred')
    window_closed()


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
        popup_w = Constants.vp_width - 200
        popup_h = Constants.vp_height - 200
        popup_x = (Constants.vp_width / 2) - (popup_w / 2) - (MeasuresDisplay.drawlist_offset / 2)
        popup_y = (Constants.vp_height / 2) - (popup_h / 2)
        with dpg.window(id='delay_window', label='Waiting...', no_title_bar=True, no_close=True, no_move=True, no_resize=True, modal=True, popup=True, width=popup_w, height=popup_h, pos=[popup_x, popup_y]):
            t = dpg.add_text(default_value='Delaying start...', pos=[popup_w / 2 - 300, popup_h / 2 - 30])
            dpg.set_item_font(item=t, font="gw2_font")
        time.sleep(1)   # initial play delay
        dpg.delete_item(item='delay_window')

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


play_time_start = -1
play_time = -1
last_tick_slots = []
last_octave = 1
def time_tick():
    global last_tick_slots
    global last_octave
    global play_time
    global play_time_start
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
            time.sleep(0.05)
    elif last_octave < prev_last_octave:
        for i in range(prev_last_octave - last_octave):
            pydirectinput.press('9')  # move down
            time.sleep(0.05)

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

    # re-enable editing after finished playing
    MouseStats.handlers_enabled = True
    main_window.controls.enable()



g_tm = None
def start_timer():
    global g_tm
    global play_time
    global play_time_start
    global last_octave
    if g_tm is None or not g_tm.alive:
        last_octave = 1
        play_time = play_time_start
        g_tm = TimeManager()
        g_tm.set_cb(time_tick, time_finished)
        g_tm.start()

        # disable editing while playing
        MouseStats.handlers_enabled = False
        main_window.controls.disable()

def stop_timer():
    global g_tm
    global play_time
    global last_tick_slots
    if g_tm is not None:
        g_tm.kill()
        # g_tm.join()
        play_time = play_time_start
    last_tick_slots.clear()

    # re-enable editing after finished playing
    MouseStats.handlers_enabled = True
    main_window.controls.enable()


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