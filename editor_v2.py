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

    def change(self):
        self.activated = not self.activated
        self.change_triggered = True

    def clear_change_trigger(self):
        self.change_triggered = False


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

    def draw(self):
        # self.clear()

        with dpg.child(parent=Elements.dpg_window, horizontal_scrollbar=True, autosize_y=True, autosize_x=True, pos=[0, 50]) as p:
            self.measures_panel = p

        for iteration, m in enumerate(self.measures):
            md = MeasureDisplay()
            md.set_data(m, iteration)
            self.measure_displays.append(md)

            md.draw(self.measures_panel)


class MeasureDisplay:
    slot_width = 30
    slot_height = 20
    slot_spacing = 4

    def __init__(self):
        self.measure = None
        self.measure_panel = None
        self.octave_panels = []
        self.measure_dl = None
        self.index = 0

    def set_data(self, d, i):
        self.measure = d
        self.index = i

    def octave_height(self):
        return len(self.measure.octaves[0].notes) * MeasureDisplay.slot_height

    def height(self):
        # num of notes * height of slot = height of octave
        # height of octave * num of octaves = height of measure
        return len(self.measure.octaves) * (self.octave_height() + 40)

    def width(self):
        num_slots = len(self.measure.octaves[0].notes[0].slots)
        return MeasureDisplay.slot_width * num_slots

    def draw(self, parent):
        print('drawing measure display')

        with dpg.child(parent=parent, width=self.width() + 40, height=self.height(), pos=[(self.width() + 40) * self.index, 0]) as m:
            self.measure_panel = m

            # draw 3 octaves
            oct0 = self.measure.octaves[0]
            with dpg.child(parent=m, height=self.octave_height() + 20, width=self.width() + 20) as op:
                with dpg.drawlist(width=self.width(), height=self.octave_height()) as dl:

                    # for each octave, draw the associated rectangles for the notes / slots
                    for note_iter, note in enumerate(oct0.notes):
                        for slot_iter, slot in enumerate(note.slots):
                            start_x = slot_iter * MeasureDisplay.slot_width
                            start_y = note_iter * MeasureDisplay.slot_height
                            dpg.draw_rectangle(
                                pmin=[start_x + (MeasureDisplay.slot_spacing / 2), start_y + (MeasureDisplay.slot_spacing / 2)],
                                pmax=[start_x + MeasureDisplay.slot_width - (MeasureDisplay.slot_spacing / 2), start_y + MeasureDisplay.slot_height - (MeasureDisplay.slot_spacing / 2)],
                                fill=[255, 255, 255, 255]
                            )

                with dpg.theme() as theme:
                    dpg.add_theme_color(target=dpg.mvThemeCol_ChildBg, value=[0, 0, 0, 0], category=dpg.mvThemeCat_Core)
                    dpg.add_theme_color(target=dpg.mvThemeCol_Border, value=[0, 0, 0, 0], category=dpg.mvThemeCat_Core)

                    dpg.set_item_theme(item=op, theme=theme)

                self.octave_panels.append(op)

            oct1 = self.measure.octaves[1]
            with dpg.child(parent=m, height=self.octave_height() + 20, width=self.width() + 20) as op:
                with dpg.drawlist(width=self.width(), height=self.octave_height()) as dl:

                    # for each octave, draw the associated rectangles for the notes / slots
                    for note_iter, note in enumerate(oct1.notes):
                        for slot_iter, slot in enumerate(note.slots):
                            start_x = slot_iter * MeasureDisplay.slot_width
                            start_y = note_iter * MeasureDisplay.slot_height
                            dpg.draw_rectangle(
                                pmin=[start_x + (MeasureDisplay.slot_spacing / 2), start_y + (MeasureDisplay.slot_spacing / 2)],
                                pmax=[start_x + MeasureDisplay.slot_width - (MeasureDisplay.slot_spacing / 2), start_y + MeasureDisplay.slot_height - (MeasureDisplay.slot_spacing / 2)],
                                fill=[255, 255, 255, 255]
                            )

                with dpg.theme() as theme:
                    dpg.add_theme_color(target=dpg.mvThemeCol_ChildBg, value=[0, 0, 0, 0], category=dpg.mvThemeCat_Core)
                    dpg.add_theme_color(target=dpg.mvThemeCol_Border, value=[0, 0, 0, 0], category=dpg.mvThemeCat_Core)

                    dpg.set_item_theme(item=op, theme=theme)

                self.octave_panels.append(op)

            oct2 = self.measure.octaves[2]
            with dpg.child(parent=m, height=self.octave_height() + 20, width=self.width() + 20) as op:
                with dpg.drawlist(width=self.width(), height=self.octave_height()) as dl:

                    # for each octave, draw the associated rectangles for the notes / slots
                    for note_iter, note in enumerate(oct2.notes):
                        for slot_iter, slot in enumerate(note.slots):
                            start_x = slot_iter * MeasureDisplay.slot_width
                            start_y = note_iter * MeasureDisplay.slot_height
                            dpg.draw_rectangle(
                                pmin=[start_x + (MeasureDisplay.slot_spacing / 2), start_y + (MeasureDisplay.slot_spacing / 2)],
                                pmax=[start_x + MeasureDisplay.slot_width - (MeasureDisplay.slot_spacing / 2), start_y + MeasureDisplay.slot_height - (MeasureDisplay.slot_spacing / 2)],
                                fill=[255, 255, 255, 255]
                            )

                with dpg.theme() as theme:
                    dpg.add_theme_color(target=dpg.mvThemeCol_ChildBg, value=[0, 0, 0, 0], category=dpg.mvThemeCat_Core)
                    dpg.add_theme_color(target=dpg.mvThemeCol_Border, value=[0, 0, 0, 0], category=dpg.mvThemeCat_Core)

                    dpg.set_item_theme(item=op, theme=theme)

                self.octave_panels.append(op)


# TODO: Don't need the panels (other than the main panel used to hold MeasuresDisplay probably)
# TODO: This will help deal with the weird spacing that the gui thinks it needs for scrolling
class MainWindow:

    def __init__(self):
        global g_measures

        self.controls = ControlBar()
        self.measures = MeasuresDisplay()
        self.measures.set_data(g_measures)

    def draw(self):
        self.controls.draw()
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

        self.pos = app_data
        print('moved: {pos}, down: {d}'.format(pos=self.pos, d=self.is_down))

        # if self.is_down:
        #     for m in g_measures:
        #         for o in m.octaves:
        #             for n in o.notes:
        #                 for s in n.slots:



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