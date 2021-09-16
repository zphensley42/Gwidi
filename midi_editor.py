import time

import dearpygui.dearpygui as dpg
import pydirectinput
import json
from dearpygui.demo import show_demo

# Harp is in C major
# notes = [
#     {'C1': '1'},
#     {'D': '2'},
#     {'E': '3'},
#     {'F': '4'},
#     {'G': '5'},
#     {'A': '6'},
#     {'B': '7'},
#     {'C2': '8'},
#     {'OctDown': '9'},
#     {'OctUp': '0'},
# ]

notes = [
    {'C2': '8'},
    {'B': '7'},
    {'A': '6'},
    {'G': '5'},
    {'F': '4'},
    {'E': '3'},
    {'D': '2'},
    {'C1': '1'},
    {'OctDown': '9'},
    {'OctUp': '0'},
]

ViewportHeight = 800
ViewportWidth = 900


# TODO: Take into account scroll amounts when delegating clicks
# TODO: use drawList for a note as it is a widget and can probably detect keys directly
# TODO: this can also help style as we could make each note a set of drawings denoting various things
# TODO: like tonguing for flute and so on
# TODO: Add octaves (measures on top of measures)

# TODO: call these 'slots'?


# TODO: Events for song completion, delay for start?


class Slot:
    spacing = 5
    width = 50
    height = 25

    def __init__(self, measure, note, index):
        self.measure = measure
        self.note = note
        self.index = index
        self.name = "slot_{m}_{n}_{i}".format(m=self.measure, n=self.note, i=self.index)
        self.rect = None
        self.child = None
        self.drawlist = None
        self.drawn = False
        self.handler = None
        self.activated = False
        self.parent = None
        self.playing = False

    def fill(self):
        return [0, 255, 0, 255] if self.activated else [255, 255, 255, 255]

    def color(self):
        return [0, 255, 0, 255] if self.playing else [255, 0, 0, 255]

    def play(self):
        self.playing = True
        self.redraw()

    def finished(self):
        self.playing = False
        self.redraw()

    def clicked_cb(self):
        print(self.name + ' clicked')
        self.activated = not self.activated

        self.drawn = False
        dpg.delete_item(self.drawlist)
        dpg.delete_item(self.child)
        self.draw(self.parent)

    def clear(self):
        self.activated = False
        self.playing = False

        self.drawn = False
        dpg.delete_item(self.drawlist)
        dpg.delete_item(self.child)
        self.draw(self.parent)

    def redraw(self):
        self.drawn = False
        dpg.delete_item(self.drawlist)
        dpg.delete_item(self.child)
        self.draw(self.parent)


    def draw(self, parent):
        self.parent = parent
        pos = [self.index * (self.width + self.spacing), 0]
        print('index: ' + str(self.index) + ', slot: ' + str(pos))

        with dpg.drawlist(parent=self.parent, width=self.width, height=self.height,
                          pos=pos) as dl:
            self.drawlist = dl
            self.rect = dpg.draw_rectangle(parent=dl, pmin=[3, 3], pmax=[self.width - 6, self.height - 6], fill=self.fill(), color=self.color(), thickness=4)

        with dpg.child(parent=self.parent, indent=0, no_scrollbar=True, label=self.name, width=self.width, height=self.height,
                       pos=pos) as obj:
            dpg.add_clicked_handler(parent=obj, callback=self.clicked_cb)
            self.child = obj

        with dpg.theme() as theme:
            dpg.add_theme_color(target=dpg.mvThemeCol_ChildBg, value=[0, 0, 0, 0], category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(target=dpg.mvThemeCol_Border, value=[0, 0, 0, 0], category=dpg.mvThemeCat_Core)

            dpg.set_item_theme(item=self.child, theme=theme)

        self.drawn = True

class SlotRow:
    def __init__(self, measure, note, index):
        self.measure = measure
        self.note = note
        self.index = index
        self.name = "row_{m}_{n}_{i}".format(m=self.measure, n=self.note, i=self.index)
        self.slots = []
        for i in range(note_basis):
            self.slots.append(Slot(self.measure, self.note, i))

    def width(self):
        return len(self.slots) * (Slot.spacing + Slot.width) + 30

    def height(self):
        return Slot.height

    def draw(self):
        with dpg.child(label=self.name, width=self.width(), height=self.height(), no_scrollbar=True,
                       pos=[0, self.index * (Slot.height + Slot.spacing)]):
            dpg.add_text(self.note, pos=[10, 0])

            with dpg.child(width=self.width() - 30, height=self.height(), no_scrollbar=True, pos=[30, 0]) as sr:
                for s in self.slots:
                    s.draw(sr)

# measure, remove the other once done
class Mes:
    def __init__(self, index, octave):
        self.index = index
        self.octave = octave
        self.rows = []
        self.name = "measure_{m}".format(m=self.index)
        for i in range(8):
            self.rows.append(SlotRow(self.index, list(notes[i].keys())[0], i))

    def height(self):
        return len(self.rows) * (Slot.height + Slot.spacing) + 10

    def width(self):
        return self.rows[-1].width()

    def draw(self):
        with dpg.child(label=self.name, width=self.width(), height=self.height(), no_scrollbar=True,
                       pos=[self.index * self.width(), self.octave * self.height()]):
            for r in self.rows:
                r.draw()


def play_callback(sender, app_data):
    print('cb_play')
    global is_playing
    is_playing = True

def stop_callback(sender, app_data):
    print('cb_stop')
    global is_playing
    is_playing = False

def save_callback(sender, app_data):
    play_completed()
    save('test.out')

def load_callback(sender, app_data):
    print('load_callback')
    play_completed()
    load('test.out')

def clear_callback(sender, app_data):
    print('clear_cb')
    play_completed()
    for m in mess:
        for r in m.rows:
            for s in r.slots:
                s.clear()

    for m in mess:
        for r in m.rows:
            for s in r.slots:
                s.redraw()

def num_measures_cb(sender, app_data):
    print('num_measures_cb: ' + str(app_data))
    dpg.set_item_user_data(tb_measures_cnt, app_data)

def apply_cb(sender, app_data):
    global tb_measures_cnt
    global measure_count
    global dpg_measures
    print('apply_cb: ' + str(sender))

    info = dpg.get_item_user_data(tb_measures_cnt)
    print('info: ' + str(info))

    measure_count = info
    init_measures()
    draw_measures()


dpg_measures = None
tb_c = None
tb_t = None
tb_dl = None
tb_r = None
tb_play = None
tb_save = None
tb_load = None
tb_clear = None
tb_measures_cnt = None
tb_apply = None
window = None
def setup_window_elements():
    global tb_c
    global tb_t
    global tb_dl
    global tb_r
    global tb_play
    global tb_save
    global tb_load
    global tb_clear
    global tb_measures_cnt
    global tb_apply
    global window

    if window is not None:
        dpg.delete_item(item=window, children_only=True)
    else:
        with dpg.window(id="MIDI_Editor", no_close=True, no_collapse=True, no_move=True, horizontal_scrollbar=True,
                        width=100, height=100) as w:
            window = w

    dpg.add_clicked_handler(parent=window, callback=play_callback)
    tb_t = dpg.add_text(parent=window, label="timebar_text", default_value='0ms', pos=[10, 20])
    tb_play = dpg.add_button(parent=window, label="Play", callback=play_callback, pos=[0, 0])
    tb_play = dpg.add_button(parent=window, label="Stop", callback=stop_callback, pos=[50, 0])
    tb_save = dpg.add_button(parent=window, label="Save", callback=save_callback, pos=[100, 0])
    tb_load = dpg.add_button(parent=window, label="Load", callback=load_callback, pos=[200, 0])
    tb_clear = dpg.add_button(parent=window, label="Clear", callback=clear_callback, pos=[300, 0])
    tb_measures_cnt = dpg.add_input_int(parent=window, default_value=4, label="# Measures", callback=num_measures_cb, pos=[400, 0], width=200)
    tb_apply = dpg.add_button(parent=window, label="Apply", callback=apply_cb, pos=[700, 0])

    # Draw the 'note' indicator for the timeline
    dpg.set_item_user_data(tb_measures_cnt, 4)
    with dpg.drawlist(parent=window, width=ViewportWidth, height=20, pos=[30, 40]) as dl:
        tb_dl = dl
        # tb_r = dpg.draw_rectangle(pmin=[0, 0], pmax=[Slot.width, 20], fill=[255, 0, 0, 255])

    draw_measures()


def draw_measures():
    global dpg_measures
    if dpg_measures is not None:
        dpg.delete_item(item=dpg_measures)

    highest_octave = 0
    for m in mess:
        if m.octave > highest_octave:
            highest_octave = m.octave
    h = mess[-1].height() * (highest_octave + 1)
    with dpg.child(parent=window, pos=[0, 50], id="measures", width=ViewportWidth, height=h + 100, horizontal_scrollbar=True) as m:
        dpg_measures = m
        for m in mess:
            m.draw()


def on_viewport_resize():
    dpg.set_item_width("measures", dpg.get_viewport_width())


note_time = 0
BPM = 122
# tempo to absolute -> 60000 / BPM
# quarter at 60 BPM = 1000 ms (1 second)
# meaning 1 measure in X/4 time is 4 seconds long

# every X ms (sixteenth notes?) increment note
# gui would use delta time to smoothly draw an increase in the position of the time-bar as a result

# TODO: All of the time / note calculation is currently based on quarter (but we need to support 16th or 32nd at least)
# TODO: note_time would just be incremented for 8 notes or 16 notes or 32 notes, etc

note_basis = 16  # 16th notes (16 notes in each measure)
def refresh_time():
    global tb_c
    global tb_t
    global tb_dl
    global tb_r
    global window
    global note_basis
    global note_time
    dpg.delete_item(item=tb_t)

    measure_index = int(note_time / note_basis)
    note_index = (note_time % note_basis)

    measures_width = int(len(mess) / 3)  # 3 octaves, we only want 1 'row'
    mid = measure_index
    if measure_index >= measures_width:
        mid = measures_width - 1
    measure = mess[mid]
    slot = measure.rows[-1].slots[note_index]

    slot_x = ((mid * note_basis) + note_index) * (Slot.width + Slot.spacing) + (mid * 30)
    # dpg.delete_item(item=tb_r)
    # tb_r = dpg.draw_rectangle(parent=tb_dl, pmin=[slot_x, 0], pmax=[slot_x + Slot.width, 50], fill=[255, 0, 0, 255])

    tb_t = dpg.add_text(parent=window, label="timebar_text",
                        default_value='{note_time}ms  mi:{mi}, ni:{ni}, slot:{slot}, slot_x:{sx}'.format(note_time=note_time, mi=measure_index, ni=note_index, slot=str(slot), sx=slot_x))

    # cx = dpg.get_x_scroll(dpg_measures)
    # dpg.set_x_scroll(dpg_measures, cx + (Slot.width))
    dpg.set_x_scroll(dpg_measures, (measure_index * 30) + (note_time * (Slot.width + Slot.spacing)))


old_time = None
is_playing = False
initial_delay_met = False
speed = 0
def update_time():
    global is_playing
    global initial_delay_met
    global note_time
    global BPM

    if not is_playing:
        return

    if not initial_delay_met:
        time.sleep(1)
        initial_delay_met = True
        return

    cur_time = time.time_ns() / 1000000

    should_play = False

    global old_time
    if old_time is None:
        old_time = time.time_ns() / 1000000
        note_time = 0
        should_play = True

    diff = cur_time - old_time
    if diff >= speed:
        note_time += 1
        old_time = cur_time
        should_play = True

    if should_play:
        play_notes()

        m_width = len(mess) / 3
        max_note = (m_width * note_basis) - 1
        print('note_time:{nt}, max:{m}'.format(nt=note_time, m=max_note))
        if note_time >= max_note:
            play_completed()

        refresh_time()


# assume we are always in octave 1 (0, 1, 2) so we can go 'down' or 'up'
# oct0 is really 'high' and oct2 is really 'low'
def play_note(slot, octave):
    global notes
    for n in notes:
        if list(n.keys())[0] == slot.note:
            if octave == 0:
                pydirectinput.press('0')
            elif octave == 2:
                pydirectinput.press('9')

            pydirectinput.press(n[slot.note])

            if octave == 0:
                pydirectinput.press('9')
            elif octave == 2:
                pydirectinput.press('0')
            break


cur_notes = []
def play_notes():
    global note_time
    global cur_notes
    # get a vertical slice of the notes to play per the current note_time
    measure_index = int(note_time / note_basis)
    note_index = (note_time % note_basis)

    octave_size = int(len(mess) / 3)

    # octave 0
    m0 = mess[measure_index + (octave_size * 0)]
    # octave 1
    m1 = mess[measure_index + (octave_size * 1)]
    # octave 2
    m2 = mess[measure_index + (octave_size * 2)]

    for s in cur_notes:
        s.finished()
    cur_notes.clear()
    for r in m0.rows:
        s = r.slots[note_index]
        s.play()
        cur_notes.append(s)
        if s.activated:
            # play
            play_note(s, 0)

    for r in m1.rows:
        s = r.slots[note_index]
        s.play()
        cur_notes.append(s)
        if s.activated:
            # play
            play_note(s, 1)

    for r in m2.rows:
        s = r.slots[note_index]
        s.play()
        cur_notes.append(s)
        if s.activated:
            # play
            play_note(s, 2)


def render_callback():
    # no-op for now, need to move the bar for real here
    v = 1
    global ViewportWidth
    vpw = dpg.get_viewport_width()
    if vpw != ViewportWidth:
        print('Vpw: ' + str(vpw))
        ViewportWidth = vpw
        # resize some stuff
        dpg.set_item_width(window, width=vpw)
        dpg.set_item_width(tb_dl, width=vpw)

    update_time()


# TODO: This octave stuff is too messy, just make a nwe structure for it to make it better probably (instead of a 1d array)
mess = []
measure_count = 4
def init_measures():
    global mess
    global measure_count
    global speed
    global note_basis

    # 60k / BPM = quarter
    # 60k * 4 / BPM = full
    # 60k * 1/2 / BPM = eighth
    # 60k * 1/4 / BPM = sixteenth
    if note_basis == 4:
        speed = int(60000 / BPM)
    if note_basis == 8:
        speed = int((60000 * 0.5) / BPM)
    if note_basis == 16:
        speed = int((60000 * 0.25) / BPM)


    mess.clear()

    oct0 = []
    oct1 = []
    oct2 = []
    for i in range(measure_count):
        oct0.append(Mes(i, 0))
        oct1.append(Mes(i, 1))
        oct2.append(Mes(i, 2))

    mess = oct0 + oct1 + oct2

def draw_editor():
    init_measures()
    setup_window_elements()
    dpg.setup_viewport()
    dpg.set_viewport_resize_callback(callback=on_viewport_resize)

    dpg.set_viewport_width(ViewportWidth)
    dpg.set_viewport_height(ViewportHeight)
    dpg.set_primary_window("MIDI_Editor", True)
    # dpg.set_viewport_resizable(False)

    # dpg.show_style_editor()

    while dpg.is_dearpygui_running():
        render_callback()
        dpg.render_dearpygui_frame()

    dpg.cleanup_dearpygui()


# Format currently just uses json
# TODO: Fix incorrect save / load logic (it is carrying across multiple measures for some reason)
def save(fname):
    octave_size = int(len(mess) / 3)
    j_out = {
        "size":"{s}".format(s=octave_size),
        "oct0":[],
        "oct1":[],
        "oct2":[],
    }

    for i in range(octave_size):
        # octave 0
        m0 = mess[i + (octave_size * 0)]
        # octave 1
        m1 = mess[i + (octave_size * 1)]
        # octave 2
        m2 = mess[i + (octave_size * 2)]

        for r in m0.rows:
            j_row = {
                    "index": r.index,
                    "slots": []
                }

            j_out['oct0'].append(j_row)

            for s in r.slots:
                j_row['slots'].append({
                    "index": s.index,
                    "val": s.activated
                })

        for r in m1.rows:
            j_row = {
                "index": r.index,
                "slots": []
            }

            j_out['oct1'].append(j_row)

            for s in r.slots:
                j_row['slots'].append({
                    "index": s.index,
                    "val": s.activated
                })

        for r in m2.rows:
            j_row = {
                "index": r.index,
                "slots": []
            }

            j_out['oct2'].append(j_row)

            for s in r.slots:
                j_row['slots'].append({
                    "index": s.index,
                    "val": s.activated
                })

    print(json.dumps(j_out))

    f = open(fname, 'w')
    f.write(json.dumps(j_out))
    f.close()


def load(fname):
    global measure_count
    f = open(fname, 'r')
    j_in = json.loads(f.read())

    # reset measures (remove and add instead?)
    for m in mess:
        for r in m.rows:
            for s in r.slots:
                s.clear()

    octave_size = int(j_in['size'])
    measure_count = octave_size
    init_measures()
    draw_measures()
    print('octave_size:' + str(octave_size))

    for i in range(octave_size):
        # octave 0
        m0 = mess[i + (octave_size * 0)]
        # octave 1
        m1 = mess[i + (octave_size * 1)]
        # octave 2
        m2 = mess[i + (octave_size * 2)]

        print('m0:{m0} m1:{m1} m2:{m2}'.format(m0=i + (octave_size * 0), m1=i + (octave_size * 1), m2=i + (octave_size * 2)))

        # oct0 in j_in has array of rows in order from measureX -> measureY

        for r_i in range(len(m0.rows)):
            r = m0.rows[r_i]
            load_r = j_in['oct0'][r_i + (i * len(m0.rows))]

            for s_i in range(len(r.slots)):
                s = r.slots[s_i]
                load_s = load_r['slots'][s_i]
                s.activated = load_s['val']

        for r_i in range(len(m1.rows)):
            r = m1.rows[r_i]
            load_r = j_in['oct1'][r_i + (i * len(m1.rows))]

            for s_i in range(len(r.slots)):
                s = r.slots[s_i]
                load_s = load_r['slots'][s_i]
                s.activated = load_s['val']

        for r_i in range(len(m2.rows)):
            r = m2.rows[r_i]
            load_r = j_in['oct2'][r_i + (i * len(m2.rows))]

            for s_i in range(len(r.slots)):
                s = r.slots[s_i]
                load_s = load_r['slots'][s_i]
                s.activated = load_s['val']

    # reset measures (remove and add instead?)
    for m in mess:
        for r in m.rows:
            for s in r.slots:
                s.redraw()




def play_completed():
    print('Play Completed!')

    global is_playing
    global initial_delay_met
    global note_time
    global old_time
    is_playing = False
    initial_delay_met = False
    note_time = 0
    old_time = None
    cur_notes.clear()
    dpg.set_x_scroll(dpg_measures, 0)
















ScaleWidth = 100
ScaleHeight = 50
ScaleSpacing = 5
