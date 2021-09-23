import time
import dearpygui.dearpygui as dpg
import dearpygui.demo
import dearpygui.logger as dpg_logger
import json
from dearpygui.demo import show_demo
import gwidi_data


class Constants:
    vp_width = 1000
    vp_height = 800
    note_labels_width = 30
    controls_width = vp_width - 35
    controls_height = 50
    content_width = vp_width - 35 - note_labels_width

    slot_width = 40
    slot_height = 20
    slot_spacing = 4
    measure_spacing = 10
    octave_spacing = 10

    @staticmethod
    def recalc_sizes(w, h):
        Constants.vp_width = w
        Constants.vp_height = h
        Constants.note_labels_width = 30
        Constants.controls_width = Constants.vp_width - 35
        Constants.controls_height = 50
        Constants.content_width = Constants.vp_width - 35 - Constants.note_labels_width

        Constants.slot_width = 40
        Constants.slot_height = 20
        Constants.slot_spacing = 4
        Constants.measure_spacing = 10
        Constants.octave_spacing = 10



class Controls:
    def draw(self, parent):
        with dpg.child(id='controls_panel', parent=parent):
            dpg.add_button(id='c_but_1', label="Button 1")
            dpg.add_same_line()
            dpg.add_dummy(width=10)
            dpg.add_same_line()
            dpg.add_button(id='c_but_2', label="Button 2")
            dpg.add_text(id='debug_text', default_value='N/A')

        self.resize()

    def resize(self):
        print('controls resize')
        dpg.configure_item(item='controls_panel', width=Constants.controls_width, height=Constants.controls_height)

class Content:
    def content_height(self):
        return len(gwidi_data.g_measure_info.notes) * Constants.slot_height + (Constants.octave_spacing * len(gwidi_data.MeasureInfo.octaves)) + 15

    def content_width(self):
        return (len(gwidi_data.g_measure_info.notes[0].slots) * Constants.slot_width) + (gwidi_data.MeasureInfo.measure_count - 1 * Constants.measure_spacing) + 30

    def draw(self, parent):
        # dpg.show_style_editor()

        scount = 0

        dpg.add_drawlist(parent=parent, id='note_labels_panel', width=Constants.note_labels_width, height=self.content_height())
        dpg.add_same_line(parent=parent)
        with dpg.child(id='content_panel', parent=parent, height=self.content_height() + 100, width=Constants.content_width, horizontal_scrollbar=True):

            with dpg.drawlist(id='content_dl', height=self.content_height() + 100, width=self.content_width()):
                for iter_n, n in enumerate(gwidi_data.g_measure_info.notes):
                    octave_index = int(iter_n / 8)
                    y_off = iter_n * Constants.slot_height + (octave_index * Constants.octave_spacing)

                    dpg.draw_text(parent='note_labels_panel', text=n.note['label'], pos=[5, y_off + 2], size=11, color=[255, 255, 255, 255])

                    for iter_s, s in enumerate(n.slots):

                        measure_index = int(iter_s / gwidi_data.MeasureInfo.slots_per_measure)

                        x_off = iter_s * Constants.slot_width + (measure_index * Constants.measure_spacing)
                        padding_offset = Constants.slot_spacing / 2
                        slot_str = 'slot{c}'.format(c=scount)
                        scount += 1
                        print('slot_str: {s}'.format(s=slot_str))
                        dpg.draw_rectangle(id=slot_str, pmin=[x_off + padding_offset, y_off + padding_offset], pmax=[x_off + Constants.slot_width - padding_offset, y_off + Constants.slot_height - padding_offset], fill=[255, 255, 255, 255])

                        if iter_s % 4 == 0 and iter_s != 0 and iter_s % 16 != 0:
                            line_pad = padding_offset * 1.5
                            dpg.draw_line(p1=[x_off, y_off + line_pad], p2=[x_off, y_off + Constants.slot_height - line_pad], thickness=2, color=[255, 0, 0, 255])

                    if iter_n % 8 == 0 and iter_n != 0:
                        line_pad = Constants.octave_spacing / 2
                        dpg.draw_line(p1=[0, y_off - line_pad], p2=[self.content_width(), y_off - line_pad], thickness=2, color=[0, 0, 200, 255])

                for s_iter, s in enumerate(gwidi_data.g_measure_info.notes[0].slots):
                    measure_index = int(s_iter / gwidi_data.MeasureInfo.slots_per_measure)

                    # Draw the scrub bar
                    y_off = self.content_height()
                    x_off = (s_iter * Constants.slot_width) + (measure_index * Constants.measure_spacing)
                    padding_offset = Constants.slot_spacing / 2
                    dpg.draw_rectangle(pmin=[x_off + padding_offset, y_off + padding_offset], pmax=[x_off + Constants.slot_width - padding_offset, y_off + Constants.slot_height - padding_offset], fill=[255, 255, 255, 255])

        self.resize()

    def detect_slot_clicked(self, pos):

        # TODO: Determine where our pos[0] (x) lies within the <---> range of slots by subdividing the range up via the 'size' of the slots
        # TODO: Need to consider the measure spacing here as well
        # TODO: Its this or we should just keep a list of these available from when we drew them and just find it that way? indexing would be faster if we could figure out the math

        # slot_x = int(pos[0] / (Constants.slot_width + Constants.measure_spacing))
        #
        # for iter_n, n in enumerate(gwidi_data.g_measure_info.notes):
        #     for iter_s, s in enumerate(n.slots):

        return None

    def detect_scrub_slot_clicked(self, pos):
        return None

    def resize(self):
        dpg.configure_item(item='content_panel', width=Constants.content_width)

class MainWindow:
    def __init__(self):
        self.controls = Controls()
        self.content = Content()

    def draw(self):
        dpg.add_window(id='MIDI_Editor', width=Constants.vp_width, height=Constants.vp_height)
        self.controls.draw('MIDI_Editor')
        self.content.draw('MIDI_Editor')

    def resize(self):
        self.controls.resize()
        self.content.resize()




def on_viewport_resize(sender, data):
    global g_window
    Constants.recalc_sizes(dpg.get_viewport_width(), dpg.get_viewport_height())
    g_window.resize()


class MouseControls:
    def __init__(self, trigger_cb):
        with dpg.handler_registry():
            self.setup_global_handlers()

        self.triggered = False
        self.trigger_cb = trigger_cb
        self.pos = dpg.get_mouse_pos()

    def handle_mouse_moved(self, sender, data):
        self.pos = dpg.get_mouse_pos()
        pos_offset = [Constants.note_labels_width, Constants.controls_height]
        if dpg.is_item_focused('content_dl'):
            pos_offset = [0, 0]

        translated_pos = [
            self.pos[0] - dpg.get_x_scroll('content_panel') - pos_offset[0],
            self.pos[1] - pos_offset[1]
        ]
        dstr = 'pos: {p}, translated_pos: {p2}, data: {d}'.format(p=self.pos, p2=translated_pos, d=data)
        dpg.configure_item(item='debug_text', default_value=dstr)

        if not self.triggered:
            return
        print('handle_mouse_moved: {d}'.format(d=self.pos))
        self.trigger_cb(translated_pos)

    def handle_mouse_down(self, sender, data):
        if self.triggered:
            return

        self.triggered = True
        self.pos = dpg.get_mouse_pos()
        print('handle_mouse_down: {d}'.format(d=self.pos))
        self.handle_mouse_moved(sender, self.pos)

    def handle_mouse_up(self, sender, data):
        self.triggered = False
        self.pos = dpg.get_mouse_pos()
        print('handle_mouse_up: {d}'.format(d=self.pos))

    def setup_global_handlers(self):
        dpg.add_mouse_move_handler(callback=self.handle_mouse_moved)
        dpg.add_mouse_down_handler(callback=self.handle_mouse_down)
        dpg.add_mouse_release_handler(callback=self.handle_mouse_up)

g_window = None
g_mouse_controls = None
def start_editor():
    global g_window
    global g_mouse_controls
    if g_window is None:
        g_window = MainWindow()
        g_mouse_controls = MouseControls(lambda pos: g_window.content.detect_slot_clicked(pos)) # for now just do a single call here

    # Default theming
    with dpg.theme(id="no_padding_theme", default_theme=True):
        dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 0, 0, category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 0, 0, category=dpg.mvThemeCat_Core)

    dpg.setup_viewport()
    dpg.set_viewport_resize_callback(callback=on_viewport_resize)

    g_window.draw()

    dpg.set_viewport_width(Constants.vp_width)
    dpg.set_viewport_height(Constants.vp_height)
    dpg.set_primary_window("MIDI_Editor", True)
    dpg.set_viewport_title("Gwidi")

    dpg.start_dearpygui()




if __name__ == '__main__':
    # midi_editor.run_editor()
    # dearpygui.demo.show_demo()
    # dpg.start_dearpygui()
    gwidi_data.init_gwidi_data()
    start_editor()