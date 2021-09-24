import time
import dearpygui.dearpygui as dpg
import dearpygui.demo
import dearpygui.logger as dpg_logger
import json
from dearpygui.demo import show_demo
import midi_importer
import gwidi_data
import play_manager

# TODO: Move scrub bar to different panel and synchronize the scrolling instead?
# TODO: Add octave selection to stats
# TODO: Move saving / loading back in
# TODO: Move macros back in
# TODO: All to remove measures from beginning as well, not just 'count' (start index)

class Constants:
    vp_width = None
    vp_height = None
    slot_width = None
    slot_height = None
    slot_spacing = None
    measure_spacing = None
    octave_spacing = None
    main_element_spacing = None
    controls_height = None
    scrub_height = None
    scrub_width = None
    content_height = None
    note_labels_width = None
    scrollbar_width = None
    controls_width = None
    content_width = None

    @staticmethod
    def recalc_sizes(w, h):
        Constants.vp_width = w
        Constants.vp_height = h

        Constants.slot_width = 40
        Constants.slot_height = 20
        Constants.slot_spacing = 4
        Constants.measure_spacing = 10
        Constants.octave_spacing = 20
        Constants.main_element_spacing = 15

        Constants.controls_height = 50
        Constants.scrub_height = Constants.slot_height * 2
        Constants.content_height = Constants.vp_height - Constants.controls_height - Constants.scrub_height*2 - (Constants.main_element_spacing * 2)

        Constants.note_labels_width = 0
        Constants.scrollbar_width = 25
        Constants.controls_width = Constants.vp_width - Constants.scrollbar_width
        Constants.content_width = Constants.vp_width - Constants.scrollbar_width
        Constants.scrub_width = Constants.vp_width - Constants.scrollbar_width

Constants.recalc_sizes(1000, 800)  # initial call


class Controls:
    def stats_saved(self, do_refresh):
        global g_window
        if do_refresh:
            g_window.refresh()
        MouseControls.enable()

    def play_finished(self):
        MouseControls.enable()
        dpg.set_item_user_data('but_play', False)
        dpg.configure_item('but_play', label='Play')

    def play_tick(self, play_time):
        measure_index = int(play_time / gwidi_data.g_measure_info.slots_per_measure)
        sx = (Constants.slot_width * play_time) + (Constants.measure_spacing * measure_index)
        dpg.set_x_scroll('content_panel', sx)

    def cb_play(self):
        print('cb_play')
        toggled_state = not dpg.get_item_user_data('but_play')
        dpg.set_item_user_data('but_play', toggled_state)
        label_str = 'Play' if not toggled_state else 'Stop'
        dpg.configure_item('but_play', label=label_str)

        if toggled_state:
            MouseControls.disable()
            play_manager.g_play_manager.play(self.play_tick, self.play_finished)
        else:
            play_manager.g_play_manager.stop()

    def cb_clear(self):
        print('clear')
        play_manager.g_play_manager.stop()
        gwidi_data.g_measure_info.clear()
        g_window.refresh()

    def cb_load(self):
        print('cb_load')

    def cb_save(self):
        print('cb_save')

    def cb_import(self):
        print('cb_import')
        MouseControls.disable()  # TODO: Need to re-enable elsewhere
        dpg.show_item("import_sel")

    def cb_macros(self):
        print('cb_macros')

    def cb_stats(self):
        print('cb_stats')
        MouseControls.disable()
        play_manager.g_play_stats.show_stats_popup(self.stats_saved)

    def cb_bpm_changed(self):
        print('cb_bpm_changed')

    def cb_measures_changed(self):
        print('cb_measures_changed')

    def draw(self, parent):
        with dpg.child(id='controls_panel', parent=parent, width=Constants.controls_width, height=Constants.controls_height):
            dpg.add_button(id='but_play', label="Play", callback=self.cb_play)
            dpg.set_item_user_data('but_play', False)
            dpg.add_same_line()
            dpg.add_dummy(width=10)
            dpg.add_same_line()
            dpg.add_button(id='but_clear', label="Clear", callback=self.cb_clear)
            dpg.add_same_line()
            dpg.add_dummy(width=10)
            dpg.add_same_line()
            dpg.add_button(id='but_load', label="Load", callback=self.cb_load)
            dpg.add_same_line()
            dpg.add_dummy(width=10)
            dpg.add_same_line()
            dpg.add_button(id='but_save', label="Save", callback=self.cb_save)
            dpg.add_same_line()
            dpg.add_dummy(width=10)
            dpg.add_same_line()
            dpg.add_button(id='but_import', label="Import", callback=self.cb_import)
            dpg.add_same_line()
            dpg.add_dummy(width=10)
            dpg.add_same_line()
            dpg.add_button(id='but_macros', label="Macros", callback=self.cb_macros)
            dpg.add_same_line()
            dpg.add_dummy(width=10)
            dpg.add_same_line()
            dpg.add_button(id='but_stats', label="Stats", callback=self.cb_stats)




            dpg.add_text(id='debug_text', default_value='N/A')

        self.resize()

    def resize(self):
        print('controls resize')
        dpg.configure_item(item='controls_panel', width=Constants.controls_width, height=Constants.controls_height)

class Content:
    def __init__(self):
        self.measure_boundaries = {}
        self.octave_boundaries = {}
        self.scrub_bar_ypos = None

    def perform_import(self, data):
        print('performing import on data: {d}'.format(d=data))

        play_manager.g_play_stats.bpm = data['bpm']

        # start filling data per the notes
        measure_index = 0
        slot_index = 0

        # notes are in order, first filter by channel
        sel_channel = data['selected_channel']

        total_measure_count = 0

        slots_to_assign = []
        for n in data['data']:
            note = data['data'][n]
            # each 'note' in data (the key) is the value of that note per the table of note values in .mid spec
            # these values combine octave + note, 'repr' pulls this out in our parsed data
            for slot in note:
                note_key = slot['repr']['note']
                note_octave = slot['repr']['octave']
                note_position = slot['position']
                note_length = slot['length']
                note_type = slot['note_type']

                gwidi_data.g_measure_info.note_vals

                print('slot info -- note_key: {nk}, note_octave: {no}, note_postion: {np}, note_length: {nl}, note_type: {nt}'.format(nk=note_key, no=note_octave, np=note_position, nl=note_length, nt=note_type))

                # convert position to slot_index
                # index the slot in gwidi_data and activate as necessary according to type
                measure_ticks = midi_importer.Utility.ticks_per_beat * 4
                ticks_per_slot = measure_ticks / gwidi_data.g_measure_info.slots_per_measure

                converted_note_index = int(note_position / ticks_per_slot)
                converted_note_length = int(note_length / ticks_per_slot)
                converted_measure_index = int((converted_note_index + converted_note_length) / gwidi_data.g_measure_info.slots_per_measure)
                if converted_measure_index > total_measure_count:
                    total_measure_count = converted_measure_index
                print('converted_note_index: {cni}, converted_note_length: {cnl}'.format(cni=converted_note_index, cnl=converted_note_length))

                slots_to_assign.append({
                    'slot_index': converted_note_index,
                    'length_indices': converted_note_length,
                    'note': note_key,
                    'octave': note_octave
                })

        total_measure_count = total_measure_count + 1   # Always at least one, need to offset 0 index
        print('New measure total: {t}'.format(t=total_measure_count))
        gwidi_data.g_measure_info.import_data(total_measure_count, slots_to_assign)
        g_window.refresh()

        MouseControls.enable()


    def content_height(self):
        return len(gwidi_data.g_measure_info.notes) * Constants.slot_height + (Constants.octave_spacing * len(gwidi_data.MeasureInfo.octaves)) + 15

    def content_width(self):
        return (len(gwidi_data.g_measure_info.notes[0].slots) * Constants.slot_width) + (gwidi_data.MeasureInfo.measure_count - 1 * Constants.measure_spacing) + 30

    def draw_slots(self):
        with dpg.drawlist(parent='content_panel', id='content_dl', height=self.content_height() + 50, width=self.content_width() + 10):
            for iter_n, n in enumerate(gwidi_data.g_measure_info.notes):
                octave_index = int(iter_n / 8)
                y_off = iter_n * Constants.slot_height + (octave_index * Constants.octave_spacing)

                # TODO: Add note_labels to the same content_dl instead
                # dpg.draw_text(parent='note_labels_panel', text=n.note['label'], pos=[5, y_off + 2], size=11,
                #               color=[255, 255, 255, 255])

                for iter_s, s in enumerate(n.slots):

                    measure_index = int(iter_s / gwidi_data.MeasureInfo.slots_per_measure)

                    x_off = iter_s * Constants.slot_width + (measure_index * Constants.measure_spacing)
                    padding_offset = 0
                    r_pos = [x_off, y_off]
                    rect = dpg.draw_rectangle(pmin=r_pos, pmax=[x_off + Constants.slot_width,
                                                                y_off + Constants.slot_height],
                                              fill=s.fill(),
                                              color=s.color(),
                                              thickness=6)
                    # print('drawing text for rect at pos: {p}, text: {t}'.format(p=dpg.get_item_pos(rect), t=s.note))
                    rect_text = dpg.draw_text(pos=[r_pos[0] + 2, r_pos[1] + 2], text=s.note['label'], size=12,
                                              color=[0, 0, 0, 255])
                    s.drawn(rect, rect_text)

                    if iter_s % gwidi_data.MeasureInfo.slots_per_measure == 0:
                        self.measure_boundaries[measure_index] = x_off

                    if iter_s % 4 == 0 and iter_s != 0 and iter_s % gwidi_data.MeasureInfo.slots_per_measure != 0:
                        line_pad = padding_offset * 1.5
                        dpg.draw_line(p1=[x_off, y_off + line_pad],
                                      p2=[x_off, y_off + Constants.slot_height - line_pad], thickness=2,
                                      color=[255, 0, 0, 255])

                if iter_n % 8 == 0:
                    self.octave_boundaries[octave_index] = y_off


            # Draw the measure labels
            for i in self.octave_boundaries:
                for j in self.measure_boundaries:
                    octave_height = Constants.slot_height * len(gwidi_data.MeasureInfo.note_vals)
                    measure_width = Constants.slot_width * gwidi_data.MeasureInfo.slots_per_measure
                    oct_bound = self.octave_boundaries[i]
                    meas_bound = self.measure_boundaries[j]

                    m_start = meas_bound
                    m_end = meas_bound + measure_width

                    o_start = oct_bound
                    o_end = oct_bound + octave_height

                    fill = [89, 88, 94, 255]
                    octave_val = len(self.octave_boundaries)-i-1
                    if octave_val in gwidi_data.g_measure_info.selected_octaves:
                        fill = [34, 115, 89, 255]
                    dpg.draw_rectangle(pmin=[m_start, o_end],
                                       pmax=[m_end, o_end + Constants.octave_spacing], fill=fill)
                    dpg.draw_text(text='Octave #{o}, Measure #{n}'.format(o=octave_val, n=j+1),
                                  pos=[m_start +(measure_width / 2) - 25, o_end + 4], size=12)

    def draw(self, parent):
        # dpg.show_style_editor()

        self.measure_boundaries = {}
        self.octave_boundaries = {}
        play_manager.g_play_manager.scrub_slots.clear()

        # dpg.add_drawlist(parent=parent, id='note_labels_panel', width=Constants.note_labels_width, height=self.content_height() + 80)
        # dpg.add_same_line(parent=parent)
        # -50 width for the scrollbar
        with dpg.child(id='content_panel', parent=parent, height=Constants.content_height, width=Constants.content_width, horizontal_scrollbar=True):
            self.draw_slots()

        self.resize()

    def refresh(self):
        dpg.delete_item('content_dl')
        self.measure_boundaries = {}
        self.octave_boundaries = {}
        self.draw_slots()

    def detect_slot_clicked(self, p):
        # use math to find the position instead of search/index for efficiency

        pos_offset = [Constants.note_labels_width, Constants.controls_height + Constants.main_element_spacing]
        translated_pos = [
            p[0] + dpg.get_x_scroll('content_panel') - pos_offset[0],
            p[1] + dpg.get_y_scroll('content_panel') - pos_offset[1]
        ]
        pos = translated_pos

        measure_width = Constants.slot_width * gwidi_data.MeasureInfo.slots_per_measure
        octave_height = Constants.slot_height * len(gwidi_data.MeasureInfo.note_vals)
        measure_boundary = None
        octave_boundary = None
        for i in self.measure_boundaries:
            boundary = self.measure_boundaries[i]

            begin = boundary
            end = begin + measure_width

            if begin <= pos[0] <= end:
                measure_boundary = {'start': begin, 'end': end, 'measure_index': i}
                break

        for i in self.octave_boundaries:
            boundary = self.octave_boundaries[i]

            begin = boundary
            end = begin + octave_height

            if begin <= pos[1] <= end:
                octave_boundary = {'start': begin, 'end': end, 'octave_index': i}
                break

        slot_index = None
        note_index = None
        if measure_boundary is not None:
            offset_pos_x = pos[0] - measure_boundary['start']

            # X/16 = offset_pos_x / measure_width
            slot_index = int((offset_pos_x * gwidi_data.MeasureInfo.slots_per_measure) / measure_width)

        if octave_boundary is not None:
            offset_pos_y = pos[1] - octave_boundary['start']

            # X/8 = offset_pos_y/octave_height
            note_index = int((offset_pos_y * len(gwidi_data.MeasureInfo.note_vals)) / octave_height)

        # use the indices to get the particular slot and act on it
        # print('pos: {p}'.format(p=pos))
        # print('measure_width: {mw}, octave_height: {oh}, measure_boundary: {mb}, octave_boundary: {ob}'.format(mw=measure_width, oh=octave_height, mb=measure_boundary, ob=octave_boundary))
        # if slot_index is not None and note_index is not None:
        #     print('slot_index: {s}, note_index: {n}'.format(s=slot_index, n=note_index))

        if measure_boundary is None or octave_boundary is None or slot_index is None or note_index is None:
            return None

        detected_slot = {'slot': slot_index, 'note': note_index, 'octave': octave_boundary['octave_index'], 'measure': measure_boundary['measure_index']}

        total_note_index = detected_slot['note'] + (detected_slot['octave'] * len(gwidi_data.MeasureInfo.note_vals))
        total_slot_index = detected_slot['slot'] + (detected_slot['measure'] * gwidi_data.MeasureInfo.slots_per_measure)

        if total_note_index >= len(gwidi_data.g_measure_info.notes):
            return None
        note = gwidi_data.g_measure_info.notes[total_note_index]

        if total_slot_index >= len(note.slots):
            return None
        slot = note.slots[total_slot_index]

        if dpg.is_mouse_button_down(0):
            # primary
            slot.activate()
        elif dpg.is_mouse_button_down(1):
            # secondary
            slot.clear()
        elif dpg.is_mouse_button_down(2):
            # tertiary
            slot.hold()

        return detected_slot

    def resize(self):
        dpg.configure_item(item='content_panel', height=Constants.content_height, width=Constants.content_width)

class ScrubBar:
    def __init__(self):
        self.scrub_bar_ypos = None

    def content_width(self):
        return (len(gwidi_data.g_measure_info.notes[0].slots) * Constants.slot_width) + (gwidi_data.MeasureInfo.measure_count - 1 * Constants.measure_spacing) + 30

    def draw_slots(self):
        with dpg.drawlist(parent='scrub_panel', id='scrub_dl', width=self.content_width() + 300, height=Constants.slot_height):
            dpg.draw_rectangle(pmin=[0, 0], pmax=[Constants.content_width, Constants.slot_height], color=[50, 50, 50, 255])
            for s_iter, s in enumerate(gwidi_data.g_measure_info.notes[0].slots):
                measure_index = int(s_iter / gwidi_data.MeasureInfo.slots_per_measure)

                # Draw the scrub bar
                y_off = 0
                x_off = (s_iter * Constants.slot_width) + (measure_index * Constants.measure_spacing)
                padding_offset = Constants.slot_spacing / 2
                selected = s_iter == play_manager.g_play_manager.play_time
                fill = [255, 0, 0, 255] if selected else [255, 255, 255, 255]
                scrub_r = dpg.draw_rectangle(pmin=[x_off + padding_offset, y_off + padding_offset],
                                             pmax=[x_off + Constants.slot_width - padding_offset,
                                                   y_off + Constants.slot_height - padding_offset],
                                             fill=fill)

                play_manager.g_play_manager.scrub_slots.append(scrub_r)

    def draw(self, parent):
        with dpg.child(parent=parent, id='scrub_panel', height=Constants.scrub_height, width=Constants.scrub_width, no_scrollbar=True):
            self.draw_slots()


    def detect_slot_clicked(self, p):
        pos_offset = [Constants.note_labels_width, Constants.controls_height + Constants.main_element_spacing + Constants.content_height + Constants.main_element_spacing]
        translated_pos = [
            p[0] + dpg.get_x_scroll('content_panel') - pos_offset[0],
            p[1] - pos_offset[1]
        ]
        pos = translated_pos

        in_scrub_bar_y = False
        if 0 <= pos[1] <= Constants.slot_height:
            # if self.scrub_bar_ypos is not None and self.scrub_bar_ypos <= pos[1] <= (self.scrub_bar_ypos + Constants.slot_height):
            in_scrub_bar_y = True

        print('pos[1]: {p1}, detect_scrub_slot_clicked, in_scrub_bar_y: {iny}, scrub_bar_ypos: {yp}'.format(p1=pos[1], iny=in_scrub_bar_y, yp=self.scrub_bar_ypos))
        if not in_scrub_bar_y:
            return None

        # Only need to determine the slot index
        measure_width = Constants.slot_width * gwidi_data.MeasureInfo.slots_per_measure
        measure_boundary = None
        for i in g_window.content.measure_boundaries:
            boundary = g_window.content.measure_boundaries[i]

            begin = boundary
            end = begin + measure_width

            if begin <= pos[0] <= end:
                measure_boundary = {'start': begin, 'end': end, 'measure_index': i}
                break


        # print('time check 1: {t}'.format(t=(time.time_ns()-o_time) / 1000000))

        slot_index = None
        if measure_boundary is not None:
            offset_pos_x = pos[0] - measure_boundary['start']

            # X/16 = offset_pos_x / measure_width
            slot_index = int((offset_pos_x * gwidi_data.MeasureInfo.slots_per_measure) / measure_width)

        if measure_boundary is None or slot_index is None:
            return None

        # print('time check 2: {t}'.format(t=(time.time_ns()-o_time) / 1000000))

        detected_slot = {'slot': slot_index, 'measure': measure_boundary['measure_index']}
        total_slot_index = detected_slot['slot'] + (detected_slot['measure'] * gwidi_data.MeasureInfo.slots_per_measure)

        # print('time check 3: {t}'.format(t=(time.time_ns()-o_time) / 1000000))

        if dpg.is_mouse_button_down(0):
            # primary
            play_manager.g_play_manager.scrub(total_slot_index)

        # print('detected_slot: {d}'.format(d=detected_slot))
        # print('time check 4: {t}'.format(t=(time.time_ns()-o_time) / 1000000))
        return detected_slot

    def refresh(self):
        dpg.delete_item('scrub_dl')
        play_manager.g_play_manager.scrub_slots.clear()
        self.draw_slots()

    def resize(self):
        dpg.configure_item('scrub_panel', height=Constants.scrub_height, width=Constants.scrub_width)

class MainWindow:
    def __init__(self):
        self.controls = Controls()
        self.content = Content()
        self.scrub_bar = ScrubBar()

        ifd = dpg.add_file_dialog(modal=True, show=False, callback=self.import_selected, id="import_sel", default_path="./../assets/midi_test/")
        dpg.add_file_extension(extension=".mid", parent=ifd)

    def import_selected(self, sender, data):
        print('import_selected: {d}'.format(d=data))
        midi_importer.show_importer(data['file_path_name'], self.content.perform_import, Constants.vp_width, Constants.vp_height)

    def close(self):
        play_manager.g_play_manager.stop()

    def draw(self):
        dpg.add_window(id='MIDI_Editor', width=Constants.vp_width, height=Constants.vp_height, no_scrollbar=True, on_close=self.close)
        self.controls.draw('MIDI_Editor')
        dpg.add_dummy(parent='MIDI_Editor', height=Constants.main_element_spacing)
        self.content.draw('MIDI_Editor')
        dpg.add_dummy(parent='MIDI_Editor', height=Constants.main_element_spacing)
        self.scrub_bar.draw('MIDI_Editor')

    def render_callback(self):
        # synchronize scrolls for 2 panels
        sx = dpg.get_x_scroll('content_panel')
        msx = dpg.get_x_scroll_max('content_panel')
        if sx <= msx:
            dpg.set_x_scroll('scrub_panel', sx)

    def refresh(self):
        self.content.refresh()
        self.scrub_bar.refresh()

    def resize(self):
        self.controls.resize()
        self.content.resize()
        self.scrub_bar.resize()

    def delegate_mouse_detect(self, pos):
        self.content.detect_slot_clicked(pos)
        self.scrub_bar.detect_slot_clicked(pos)



def on_viewport_resize(sender, data):
    global g_window
    Constants.recalc_sizes(dpg.get_viewport_width(), dpg.get_viewport_height())
    g_window.resize()


class MouseControls:
    controls_enabled = True

    @staticmethod
    def enable():
        MouseControls.controls_enabled = True

    @staticmethod
    def disable():
        MouseControls.controls_enabled = False

    def __init__(self, trigger_cb):
        with dpg.handler_registry():
            self.setup_global_handlers()

        self.triggered = False
        self.trigger_cb = trigger_cb

    def handle_mouse_moved(self, sender, data):
        if not MouseControls.controls_enabled:
            return


        self.pos = data

        # ignore clicks on the control bar
        if self.pos[1] < Constants.controls_height:
            return

        dstr = 'pos: {p}, data: {d}'.format(p=self.pos, d=data)
        dpg.configure_item(item='debug_text', default_value=dstr)

        if not self.triggered:
            return
        # print('handle_mouse_moved: {d}'.format(d=self.pos))
        self.trigger_cb(self.pos)

    def handle_mouse_down(self, sender, data):
        if not MouseControls.controls_enabled:
            return

        if self.triggered:
            return

        self.triggered = True
        # print('handle_mouse_down: {d}'.format(d=self.pos))
        self.handle_mouse_moved(sender, self.pos)

    def handle_mouse_up(self, sender, data):
        if not MouseControls.controls_enabled:
            return

        self.triggered = False
        # print('handle_mouse_up: {d}'.format(d=self.pos))
        for n in gwidi_data.g_measure_info.notes:
            for s in n.slots:
                s.change_finished()

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
        g_mouse_controls = MouseControls(lambda pos: g_window.delegate_mouse_detect(pos))

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

    while dpg.is_dearpygui_running():
        g_window.render_callback()
        dpg.render_dearpygui_frame()

    dpg.cleanup_dearpygui()




if __name__ == '__main__':
    # midi_editor.run_editor()
    # dearpygui.demo.show_demo()
    # dpg.start_dearpygui()
    gwidi_data.init_gwidi_data()
    play_manager.init_play_manager()
    start_editor()