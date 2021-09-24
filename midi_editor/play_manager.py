import dearpygui.dearpygui as dpg
import gwidi_data

class PlayStats:
    def __init__(self):
        self.bpm = 120
        self.cb_closed = None

    def assign_bpm(self, b):
        self.bpm = b

    def cb_input_changed(self, sender, data):
        dpg.set_item_user_data(sender, data)

    def cb_close(self, do_save):
        if do_save:
            self.bpm = dpg.get_item_user_data(item='bpm_cnt')
            gwidi_data.MeasureInfo.update_measure_count(dpg.get_item_user_data(item='measure_cnt'))

            # TODO: Refresh song playback here (i.e. refresh our measures and stop the playback mechanism)

        dpg.delete_item('song_stats')

        if self.cb_closed is not None:
            self.cb_closed(do_save)

    def show_stats_popup(self, cb_closed):
        self.cb_closed = cb_closed

        # TODO: Don't allow mouse delegation while popped up
        w_space = dpg.get_viewport_width() - 300
        with dpg.window(pos=[w_space / 2, 0], width=300, id='song_stats', popup=True, modal=True, no_close=True, no_title_bar=True, no_move=True, no_resize=True):
            dpg.add_dummy(height=20)

            dpg.add_dummy(width=20)
            dpg.add_same_line()
            dpg.add_input_int(id='bpm_cnt', label='BPM', default_value=self.bpm, callback=self.cb_input_changed)
            dpg.add_same_line()
            dpg.add_dummy(width=20)

            dpg.add_dummy(height=10)
            dpg.add_dummy(width=20)
            dpg.add_same_line()
            dpg.add_input_int(id='measure_cnt', label="# Measures", default_value=gwidi_data.g_measure_info.measure_count, callback=self.cb_input_changed)
            dpg.add_same_line()
            dpg.add_dummy(width=20)

            dpg.add_dummy(height=20)
            dpg.add_dummy(width=100)
            dpg.add_same_line()
            with dpg.group(horizontal=True, horizontal_spacing=20):
                dpg.add_button(label='Save', callback=lambda: self.cb_close(True))
                dpg.add_button(label='Cancel', callback=lambda: self.cb_close(False))
            dpg.add_dummy(height=20)

class PlayManager:
    def __init__(self):
        self.play_time = 0
        self.scrub_slots = []

    def scrub(self, play_time):
        self.play_time = play_time
        for s_iter, s in enumerate(self.scrub_slots):
            selected = s_iter == self.play_time
            fill = [255, 0, 0, 255] if selected else [255, 255, 255, 255]
            dpg.configure_item(s, fill=fill)


g_play_manager = None
g_play_stats = None
def init_play_manager():
    global g_play_manager
    global g_play_stats
    if g_play_manager is None:
        g_play_manager = PlayManager()

    if g_play_stats is None:
        g_play_stats = PlayStats()
