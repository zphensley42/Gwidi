import time
import dearpygui.dearpygui as dpg
import json
from dearpygui.demo import show_demo
import pydirectinput
import keyboard
import threading


pydirectinput.PAUSE = 0


# TODO: Drawn / Loading states for when we are waiting for things to finish drawing
# TODO: List of songs / files for save/load
# TODO: Macros
# TODO: difference between 'strung' notes and 'held' notes so that the tabs can look closer to the MIDI
# TODO: Fix clearing taking so long?
# TODO: refresh measures -> load fails to do anything


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


class Elements:
    dpg_window = None


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

# TODO: Some timing issues with clear / load / etc freezing the UI (and sleeps for playback doing similar when going between octaves?)
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

    def clear(self):
        if self.control_bar is not None:
            dpg.delete_item(self.control_bar)
            self.control_bar = None

    def width(self):
        return dpg.get_viewport_width()

    def height(self):
        return 50

    def cb_play(self, sender, app_data):
        print('cb_play')

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

    def cb_apply(self, sender, app_data):
        cnt = dpg.get_item_user_data(self.measure_cnt_ctrl)
        Constants.measures_count = cnt
        init_measures(cnt)
        main_window.refresh_measures()
        main_window.draw()

    def cb_save(self, sender, app_data):
        print('cb_save')
        save('test_save.out')

    def cb_load(self, sender, app_data):
        print('cb_load')
        load('test.out')

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
        clear_measures()
        main_window.refresh_measures()
        main_window.draw()

    def draw(self):
        # self.clear()

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
        self.measures = []
        self.measure_displays = []

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

    def draw(self):
        # self.clear()

        with dpg.child(parent=Elements.dpg_window, horizontal_scrollbar=True, autosize_y=True, autosize_x=True, pos=[0, 100]) as p:
            self.measures_panel = p
            with dpg.drawlist(pos=[MeasuresDisplay.drawlist_offset, 0], width=self.content_width(), height=self.content_height() + 50) as dl:
                for iteration, m in enumerate(self.measures):
                    md = MeasureDisplay()
                    md.set_data(m, iteration)
                    self.measure_displays.append(md)

                    md.draw(dl)


class MeasureDisplay:
    slot_width = 30
    slot_height = 20
    slot_spacing = 4

    octave_spacing = 20
    measure_spacing = 10

    def __init__(self):
        self.measure = None
        self.measure_panel = None
        self.octave_panels = []
        self.measure_dl = None
        self.index = 0

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
                print('drawing text: ' + slot.note_key['label'])
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

    def draw(self, parent):
        print('drawing measure display')

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



# TODO: Don't need the panels (other than the main panel used to hold MeasuresDisplay probably)
# TODO: This will help deal with the weird spacing that the gui thinks it needs for scrolling
class MainWindow:

    def __init__(self):
        self.controls = None
        self.info = None
        self.measures = None
        self.note_labels = None
        self.refresh_measures()

    def clear(self):
        dpg.delete_item(Elements.dpg_window, children_only=True)

    def refresh_measures(self):
        global g_measures

        self.controls = ControlBar()
        self.info = InfoBar()
        self.measures = MeasuresDisplay()
        self.measures.set_data(g_measures)
        self.note_labels = NoteLabels()

    def draw(self):
        self.clear()

        self.controls.draw()
        self.info.draw()
        self.measures.draw()
        self.note_labels.draw()


def on_viewport_resize():
    print('viewport resized: {w}x{h}'.format(w=dpg.get_viewport_width(), h=dpg.get_viewport_height()))


def render_callback():
    # print('render loop called')
    x = 1


g_measures = []
def init_measures(count):
    global g_measures
    g_measures.clear()
    for i in range(count):
        g_measures.append(Measure())

def clear_measures():
    for m in g_measures:
        for o in m.octaves:
            for n in o.notes:
                for s in n.slots:
                    s.clear()

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

                    if slot.activated:
                        if write_delim:
                            f.write('-')

                        f.write('o{ov}n{nv}'.format(ov=slot.note_octave, nv=slot.note_key['key']))
                        write_delim = True

            f.write(']')


def load(fname):
    global g_measures
    global main_window
    clear_measures()

    f = open(fname, 'r')
    song_info = f.read()

    # 130[o0n1-o0n5-o1n3-o2n4]
    # BPM[<--> note info]
    #    [octave+note-octave+note-etc]

    # parse the info
    first_index = song_info.index('[')
    bpm = song_info[0:first_index]
    notes = song_info[first_index:]

    print('load, bpm: ' + bpm)
    print('load, notes: ' + notes)

    parsed_measures = [Measure()]
    measure_index = 0
    slot_index = 0

    while len(notes) > 0:
        print('len: ' + str(len(notes)))

        range_begin = notes.index('[')
        range_end = notes.index(']')
        range = notes[range_begin+1:range_end]

        print('parse info: {rb} {re} {r}'.format(rb=range_begin, re=range_end, r=range))

        # do something with the info
        if slot_index >= Constants.slots_per_measure:
            measure_index += 1
            slot_index = 0
            parsed_measures.append(Measure())
            print('new measure')

        if range_end == (range_begin + 1):
            notes = notes[range_end + 1:]
            print('new notes: ' + notes)

            slot_index += 1
            continue

        # TODO: Sanitization of parsed values instead of just crashing for bad indices
        octave_notes = range.split('-')
        for on in octave_notes:
            # first 2 chars are the octave indicator
            oct_ind = on[0:2]
            # second 2 chars are the note indicator
            note_ind = on[2:4]

            print('oct_ind: {oi}, note_ind: {ni}'.format(oi=oct_ind, ni=note_ind))

            oct_val = int(oct_ind[1])
            note_val = note_ind[1]

            print('oct_val: {ov}, note_val: {nv}'.format(ov=oct_val, nv=note_val))
            print('parsed_measures: ' + str(parsed_measures))

            selected_oct = None
            for o in parsed_measures[measure_index].octaves:
                if o.octave_val == oct_val:
                    selected_oct = o
                    break
            if selected_oct is not None:
                for n in selected_oct.notes:
                    if n.note['key'] == note_val:
                        n.slots[slot_index].activated = True
                        break

        notes = notes[range_end+1:]
        print('new notes: ' + notes)

        slot_index += 1

    # after building our parsed measures, replace our g_measures and draw
    Constants.measures_count = len(parsed_measures)
    TimeManager.BPM = int(bpm)

    g_measures = parsed_measures
    print_measures()
    main_window.refresh_measures()
    main_window.draw()


class MouseStats:
    is_down = False
    is_down_secondary = False
    is_down_tertiary = False
    pos = None

    def moved(self, sender, app_data):
        global g_measures
        global main_window

        self.pos = app_data
        # print('moved: {pos}, down: {d}'.format(pos=self.pos, d=self.is_down))

        translated_mouse_pos = [
            self.pos[0] + dpg.get_x_scroll(main_window.measures.measures_panel),
            self.pos[1] + dpg.get_y_scroll(main_window.measures.measures_panel) - dpg.get_item_pos(main_window.measures.measures_panel)[1],
        ]

        main_window.info.set_mouse_pos(self.pos)
        main_window.info.set_translated_mouse_pos(translated_mouse_pos)

        type = 0 if self.is_down else 1 if self.is_down_secondary else 2 if self.is_down_tertiary else -1
        # print('type: ' + str(type))
        if self.is_down or self.is_down_secondary or self.is_down_tertiary:
            for mdisplay in main_window.measures.measure_displays:
                mdisplay.delegate_mouse_down(translated_mouse_pos, type)



    def downed(self, sender, app_data):
        if self.is_down or self.is_down_secondary or self.is_down_tertiary:
            return

        # primary
        primary_down = dpg.is_mouse_button_down(0)

        # secondary
        secondary_down = dpg.is_mouse_button_down(1)

        # tertiary
        tertiary_down = dpg.is_mouse_button_down(2)

        print('downed')
        if primary_down:
            self.is_down = True
        elif secondary_down:
            self.is_down_secondary = True
        elif tertiary_down:
            self.is_down_tertiary = True

        self.moved(sender, self.pos)

    def upped(self):
        if not self.is_down and not self.is_down_secondary and not self.is_down_tertiary:
            return

        print('upped')
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

    init_measures(3)

    Elements.dpg_window = dpg.add_window(id='MIDI_Editor', width=Constants.vp_width, height=Constants.vp_height)
    dpg.setup_viewport()
    with dpg.handler_registry():
        setup_global_handlers()
    dpg.set_viewport_resize_callback(callback=on_viewport_resize)

    if main_window is None:
        main_window = MainWindow()
        main_window.draw()

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
        print('TimeManager tick')
        if self.tick_cb is not None:
            self.tick_cb()

    def kill(self):
        self.alive = False
        # self.join()


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
        last_octave = 1
        oct_found = m.octaves[1]

    print('last_octave: {lo}   prev_last_octave: {plo}'.format(lo=last_octave, plo=prev_last_octave))

    # 'switch' octaves as necessary
    if last_octave > prev_last_octave:
        for i in range(last_octave - prev_last_octave):
            pydirectinput.press('0')  # move up
            time.sleep(0.1)
    elif last_octave < prev_last_octave:
        for i in range(prev_last_octave - last_octave):
            pydirectinput.press('9')  # move down
            time.sleep(0.1)

    # 'play' them all
    for n in oct_found.notes:
        s = n.slots[slot_index]
        s.play()
        last_tick_slots.append(s)

    # assign our scroll
    scroll_width = (main_window.measures.measure_displays[0].measure_width() * measure_index) + (slot_index * MeasureDisplay.slot_width)
    print('scroll_width: ' + str(scroll_width) + '   mi: ' + str(measure_index) + '   si: ' + str(slot_index))
    dpg.set_x_scroll(main_window.measures.measures_panel, scroll_width)


def time_finished():
    dpg.set_item_user_data(main_window.controls.play_pause, False)
    dpg.set_item_label(main_window.controls.play_pause, "Play")
    dpg.set_x_scroll(main_window.measures.measures_panel, 0)


g_tm = None
def start_timer():
    global g_tm
    global play_time
    if g_tm is None or not g_tm.alive:
        play_time = -1
        g_tm = TimeManager()
        g_tm.set_cb(time_tick, time_finished)
        g_tm.start()

def stop_timer():
    global g_tm
    global play_time
    if g_tm is not None:
        g_tm.kill()
        # g_tm.join()
        play_time = -1


def print_measures():
    for m in g_measures:
        for o in m.octaves:
            print('octave' + str(o.octave_val))
            for n in o.notes:
                print('note' + str(n.note))
                for s in n.slots:
                    print('slot' + str(s.activated))

    print('measures: ' + str(g_measures))


if __name__ == '__main__':
    # midi_editor.run_editor()
    start_editor()
    # keyboard.wait()