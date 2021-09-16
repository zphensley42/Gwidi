import time
import dearpygui.dearpygui as dpg
import json
from dearpygui.demo import show_demo
import pydirectinput
import keyboard


class Constants:
    vp_width = 800
    vp_height = 600

    slots_per_measure = 16

    notes = [
        {'C2': '8'},
        {'B': '7'},
        {'A': '6'},
        {'G': '5'},
        {'F': '4'},
        {'E': '3'},
        {'D': '2'},
        {'C1': '1'},
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


class Slot:

    def __init__(self):
        self.activated = False
        self.playing = False
        self.drawn = False
        self.change_triggered = False
        self.rect = None

    def set_rect(self, r):
        self.rect = r

    def change(self):
        if self.change_triggered:
            return

        self.activated = not self.activated
        self.change_triggered = True

        dpg.configure_item(self.rect, fill=self.fill())

    def clear_change_trigger(self):
        self.change_triggered = False

    def fill(self):
        return [0, 255, 0, 255] if self.activated else [255, 255, 255, 255]


class Note:

    def __init__(self, note):
        self.note = note
        self.slots = []
        for i in range(Constants.slots_per_measure):
            self.slots.append(Slot())


class Octave:

    def __init__(self, octave_val):
        self.octave_val = octave_val
        self.notes = []
        for i in range(len(Constants.notes)):
            note = Constants.notes[i]
            self.notes.append(Note(note))


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
        self.save = None
        self.load = None

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

        l = "Play" if not toggled else "Pause"
        dpg.set_item_label(self.play_pause, label=l)

    def cb_save(self, sender, app_data):
        print('cb_save')

    def cb_load(self, sender, app_data):
        print('cb_load')

    def draw(self):
        # self.clear()

        with dpg.child(parent=Elements.dpg_window, pos=[0, 0], autosize_x=True, autosize_y=True) as c:
            self.control_bar = c
            self.play_pause = dpg.add_button(label="Play", callback=self.cb_play, pos=[0, 0], height=self.height(), width=50)
            dpg.set_item_user_data(self.play_pause, False)

            self.save = dpg.add_button(label="Save", callback=self.cb_save, pos=[60, 0], height=self.height(), width=50)
            self.load = dpg.add_button(label="Load", callback=self.cb_load, pos=[120, 0], height=self.height(), width=50)


class InfoBar:
    def __init__(self):
        self.data_label = 'Debug_Info: '
        self.mouse_pos = []
        self.translated_mouse_pos = []
        self.data_text = None

    def refresh(self):
        dpg.configure_item(self.data_text, default_value=self.data_string())

    def set_mouse_pos(self, mouse_pos):
        self.mouse_pos = mouse_pos
        self.refresh()

    def set_translated_mouse_pos(self, mouse_pos):
        self.translated_mouse_pos = mouse_pos
        self.refresh()

    def data_string(self):
        return "{label} mouse_pos: {mp} translated: {mp2}".format(
            label=self.data_label,
            mp=self.mouse_pos,
            mp2=self.translated_mouse_pos,
        )

    def draw(self):
        global main_window
        self.data_text = dpg.add_text(parent=Elements.dpg_window, pos=[10, 65], default_value=self.data_string())


class MeasuresDisplay:
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
            with dpg.drawlist(width=self.content_width(), height=self.content_height() + 50) as dl:
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
                start_x = x_off + slot_iter * MeasureDisplay.slot_width
                start_y = y_off + note_iter * MeasureDisplay.slot_height
                r = dpg.draw_rectangle(
                    pmin=[start_x + (MeasureDisplay.slot_spacing / 2), start_y + (MeasureDisplay.slot_spacing / 2)],
                    pmax=[start_x + MeasureDisplay.slot_width - (MeasureDisplay.slot_spacing / 2),
                          start_y + MeasureDisplay.slot_height - (MeasureDisplay.slot_spacing / 2)],
                    fill=slot.fill()
                )
                slot.set_rect(r)

    def delegate_mouse_down(self, pos):
        global main_window

        # Things to care about when determining what rect we are in:
        # 'window' position (top-left corner) on the screen: dpg.get_viewport_pos()
        # scroll offset of the measures display child

        # self.index is the index of the measure we are
        slot_found = None
        for oct_ind, oct in enumerate(self.measure.octaves):
            if slot_found is not None:
                break

            x_off = self.index * (self.measure_width() + MeasureDisplay.measure_spacing)
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

        print('slot_found: {s}'.format(s=str(slot_found)))
        if slot_found is not None:
            slot_found.change()

    def draw(self, parent):
        print('drawing measure display')

        # draw 3 octaves
        self.draw_octave(parent, self.index, 0)
        self.draw_octave(parent, self.index, 1)
        self.draw_octave(parent, self.index, 2)


# TODO: Don't need the panels (other than the main panel used to hold MeasuresDisplay probably)
# TODO: This will help deal with the weird spacing that the gui thinks it needs for scrolling
class MainWindow:

    def __init__(self):
        global g_measures

        self.controls = ControlBar()
        self.info = InfoBar()
        self.measures = MeasuresDisplay()
        self.measures.set_data(g_measures)

    def draw(self):
        self.controls.draw()
        self.info.draw()
        self.measures.draw()


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


class MouseStats:
    is_down = False
    pos = None

    def moved(self, sender, app_data):
        global g_measures
        global main_window

        self.pos = app_data
        print('moved: {pos}, down: {d}'.format(pos=self.pos, d=self.is_down))

        translated_mouse_pos = [
            self.pos[0] + dpg.get_x_scroll(main_window.measures.measures_panel),
            self.pos[1] + dpg.get_y_scroll(main_window.measures.measures_panel) - dpg.get_item_pos(main_window.measures.measures_panel)[1],
        ]

        main_window.info.set_mouse_pos(self.pos)
        main_window.info.set_translated_mouse_pos(translated_mouse_pos)

        if self.is_down:
            for mdisplay in main_window.measures.measure_displays:
                mdisplay.delegate_mouse_down(translated_mouse_pos)



    def downed(self):
        if self.is_down:
            return

        print('downed')
        self.is_down = True

    def upped(self):
        if not self.is_down:
            return

        print('upped')
        self.is_down = False

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


if __name__ == '__main__':
    # midi_editor.run_editor()
    start_editor()
    # keyboard.wait()