import dearpygui.dearpygui as dpg
import gwidi_data
import threading, time
import event_queue


from sys import platform
if platform == "linux" or platform == "linux2":
    print('linux not tested currently')
elif platform == "darwin":
    import keyboard
    class pydirectinput:
        @staticmethod
        def press(key):
            keyboard.press_and_release(key)
elif platform == "win32":
    import pydirectinput
    pydirectinput.PAUSE = 0

class PlayStats:
    def __init__(self):
        self.bpm = 120
        self.cb_closed = None
        self.default_octave = 1
        self.sounds_enabled = False
        self.samples_dir = './../assets/samples'

        # options: HighestOctave, LowestOctave, HighestActiveSlots, SpecifiedDefault
        self.octave_pick_mode = 'HighestOctave'

    def assign_bpm(self, b):
        self.bpm = b

    def cb_input_changed(self, sender, data):
        dpg.set_item_user_data(sender, data)

    def cb_close(self, do_save):
        if do_save:
            self.bpm = dpg.get_item_user_data(item='bpm_cnt')
            gwidi_data.MeasureInfo.update_measure_count(dpg.get_item_user_data(item='measure_cnt'))

            gwidi_data.MeasureInfo.selected_octaves[0] = dpg.get_item_user_data(item='octave_0_sel')
            gwidi_data.MeasureInfo.selected_octaves[1] = dpg.get_item_user_data(item='octave_1_sel')
            gwidi_data.MeasureInfo.selected_octaves[2] = dpg.get_item_user_data(item='octave_2_sel')

        dpg.delete_item('song_stats')

        if self.cb_closed is not None:
            self.cb_closed(do_save)

    def show_stats_popup(self, cb_closed):
        self.cb_closed = cb_closed

        # TODO: Don't allow mouse delegation while popped up
        w_space = dpg.get_viewport_width() - 300
        with dpg.window(pos=[w_space / 2, 0], width=300, height=250, id='song_stats', popup=True, modal=True, no_close=True, no_title_bar=True, no_move=True, no_resize=True):
            dpg.add_dummy(height=20)

            dpg.add_dummy(width=20)
            dpg.add_same_line()
            dpg.add_input_int(id='bpm_cnt', label='BPM', default_value=self.bpm, callback=self.cb_input_changed, max_value=300, min_value=1)
            dpg.set_item_user_data('bpm_cnt', self.bpm)
            dpg.add_same_line()
            dpg.add_dummy(width=20)

            dpg.add_dummy(height=10)
            dpg.add_dummy(width=20)
            dpg.add_same_line()
            dpg.add_input_int(id='measure_cnt', label="# Measures", default_value=gwidi_data.g_measure_info.measure_count, callback=self.cb_input_changed, min_value=1)
            dpg.set_item_user_data('measure_cnt', gwidi_data.g_measure_info.measure_count)
            dpg.add_same_line()
            dpg.add_dummy(width=20)

            dpg.add_dummy(height=10)
            dpg.add_dummy(width=20)
            dpg.add_same_line()
            dpg.add_input_int(width=100, id='octave_0_sel', label="Octave 0 Mapping", default_value=gwidi_data.g_measure_info.selected_octaves[0], callback=self.cb_input_changed)
            dpg.set_item_user_data('octave_0_sel', gwidi_data.g_measure_info.selected_octaves[0])
            dpg.add_same_line()
            dpg.add_dummy(width=20)

            dpg.add_dummy(height=10)
            dpg.add_dummy(width=20)
            dpg.add_same_line()
            dpg.add_input_int(width=100, id='octave_1_sel', label="Octave 1 Mapping", default_value=gwidi_data.g_measure_info.selected_octaves[1], callback=self.cb_input_changed)
            dpg.set_item_user_data('octave_1_sel', gwidi_data.g_measure_info.selected_octaves[1])
            dpg.add_same_line()
            dpg.add_dummy(width=20)

            dpg.add_dummy(height=10)
            dpg.add_dummy(width=20)
            dpg.add_same_line()
            dpg.add_input_int(width=100, id='octave_2_sel', label="Octave 2 Mapping", default_value=gwidi_data.g_measure_info.selected_octaves[2], callback=self.cb_input_changed)
            dpg.set_item_user_data('octave_2_sel', gwidi_data.g_measure_info.selected_octaves[2])
            dpg.add_same_line()
            dpg.add_dummy(width=20)

            dpg.add_dummy(height=20)
            dpg.add_dummy(width=100)
            dpg.add_same_line()
            with dpg.group(horizontal=True, horizontal_spacing=20):
                dpg.add_button(label='Save', callback=lambda: self.cb_close(True))
                dpg.add_button(label='Cancel', callback=lambda: self.cb_close(False))
            dpg.add_dummy(height=20)


class PlayThread(threading.Thread):
    BPM = 120

    # 60k / BPM = quarter
    # 60k * 4 / BPM = full
    # 60k * 1/2 / BPM = eighth
    # 60k * 1/4 / BPM = sixteenth
    # mult = 4 / gwidi_data.MeasureInfo.slots_per_measure

    def __init__(self):
        self.tick_cb = None
        self.finished_cb = None
        self.mult = 4 / gwidi_data.MeasureInfo.slots_per_measure
        self.speed = (60 * self.mult) / g_play_stats.bpm

        self.alive = True
        threading.Thread.__init__(self)

    def show_initial_popup(self):
        vpw = dpg.get_viewport_width()
        vph = dpg.get_viewport_height()
        popup_w = vpw - 200
        popup_h = vph - 200
        popup_x = (vpw / 2) - (popup_w / 2)
        popup_y = (vph / 2) - (popup_h / 2)
        with dpg.window(id='delay_window', label='Waiting...', no_title_bar=True, no_close=True, no_move=True, no_resize=True, modal=True, popup=True, width=popup_w, height=popup_h, pos=[popup_x, popup_y]):
            t = dpg.add_text(default_value='Delaying start...', pos=[popup_w / 2 - 300, popup_h / 2 - 30])
            # dpg.set_item_font(item=t, font="gw2_font")

    def start(self, t_cb, f_cb):
        self.tick_cb = t_cb
        self.finished_cb = f_cb

        threading.Thread.start(self)

    def run(self):
        self.show_initial_popup()
        time.sleep(1)   # initial play delay
        dpg.delete_item(item='delay_window')

        while self.alive:
            time.sleep(self.speed)
            self.tick()

        if self.finished_cb is not None:
            self.finished_cb()

    def tick(self):
        if self.alive and self.tick_cb is not None:
            self.tick_cb()

    def kill(self):
        self.alive = False


class PlayManager:
    def __init__(self):
        self.play_time = 0
        self.play_time_start = 0
        self.scrub_slots = []
        self.last_played = []
        self.last_played_octave = 1

        self.play_thread = None
        self.play_finished_cb = None

        self.sample_manager = None

    def scrub(self, t):
        # reconfigure the old first
        dpg.configure_item(self.scrub_slots[self.play_time_start], fill=[255, 255, 255, 255])

        # then the new second
        self.play_time_start = t
        dpg.configure_item(self.scrub_slots[self.play_time_start], fill=[255, 0, 0, 255])

    def active_slots_in_octave(self, notes, slot_index, octave):
        return len(list(filter(lambda n: n.octave == octave and n.slots[slot_index].activated, notes)))

    def play_slot(self, slot):
        print('playing slot: {s}'.format(s=slot))

        note_to_play = slot.note
        self.sample_manager.push_sample({'key': note_to_play['key'], 'note': note_to_play['label'], 'octave': slot.octave})

    def select_slots_by_mode(self, in_slots):
        octave = g_play_stats.default_octave
        to_play = in_slots[list(in_slots.keys())[octave]]

        if g_play_stats.octave_pick_mode == 'HighestOctave':
            for iter, c in enumerate(in_slots):
                slots = in_slots[c]
                if len(slots) > 0:
                    octave = c
                    return {'slots': slots, 'octave_ind': iter}  # first entry should be highest octave
        elif g_play_stats.octave_pick_mode == 'LowestOctave':
            # TODO: Fill-in
            return []
        elif g_play_stats.octave_pick_mode == 'HighestActiveSlots':
            for iter, c in enumerate(in_slots):
                slots = in_slots[c]
                if len(slots) > len(to_play):
                    octave = c
                    to_play = {'slots': slots, 'octave_ind': iter}
            return to_play
        elif g_play_stats.octave_pick_mode == 'SpecifiedDefault':
            # TODO: Fill-in
            return []

        return {'slots': to_play, 'octave_ind': octave}

    def tick(self):
        self.play_time += 1

        ot = time.time_ns()
        print('time check 0: {t}'.format(t=(time.time_ns() - ot) / 1000000))

        if self.play_time >= (gwidi_data.g_measure_info.measure_count * gwidi_data.g_measure_info.slots_per_measure):
            self.finish()
            return

        # TODO: This should also be moved to the UI event thread as it makes UI changes
        print('play_time: {p}'.format(p=self.play_time))
        event_queue.g_event_queue.push_msg({'what': 4, 'desc': 'update_notes_finished_playing', 'params': {'slots': self.last_played.copy()}})
        self.last_played.clear()

        print('time check 1: {t}'.format(t=(time.time_ns() - ot) / 1000000))

        # each play_time, determine the desired octave via what notes are available (and the default)
        octaves = gwidi_data.g_measure_info.selected_octaves
        cur_slots = {}

        print('time check 2: {t}'.format(t=(time.time_ns() - ot) / 1000000))

        for o in octaves:
            cur_slots[o] = []
            for n in gwidi_data.g_measure_info.notes:
                slot = n.slots[self.play_time]
                if n.octave == o and slot.activated:
                    cur_slots[o].append(slot)

        print('time check 3: {t}'.format(t=(time.time_ns() - ot) / 1000000))

        to_play = self.select_slots_by_mode(cur_slots)

        print('time check 4: {t}'.format(t=(time.time_ns() - ot) / 1000000))

        print('selected_octaves: {p0}, cur_slots: {p1}, to_play: {p2}'.format(p0=octaves, p1=cur_slots, p2=to_play))

        # 'switch' octaves as necessary
        # TODO: This should be part of the 'play_slot' logic instead to not mess with timing here? (maybe)
        # TODO: There is some weird reverse indexing I've done somewhere with octaves that is making me reverse again here
        if to_play['octave_ind'] > self.last_played_octave:
            for i in range(to_play['octave_ind'] - self.last_played_octave):
                print('moving octave down')
                pydirectinput.press('9')  # move down
                time.sleep(0.01)
        elif to_play['octave_ind'] < self.last_played_octave:
            for i in range(self.last_played_octave - to_play['octave_ind']):
                print('moving octave up')
                pydirectinput.press('0')  # move up
                time.sleep(0.01)

        print('time check 5: {t}'.format(t=(time.time_ns() - ot) / 1000000))

        for s in to_play['slots']:
            self.play_slot(s)
            self.last_played.append(s)
        self.last_played_octave = to_play['octave_ind']

        event_queue.g_event_queue.push_msg({'what': 3, 'desc': 'update_notes_playing', 'params': {'slots': self.last_played.copy()}})

        print('time check 6: {t}'.format(t=(time.time_ns() - ot) / 1000000))

        # update the playout on scrub
        event_queue.g_event_queue.push_msg({'what': 1, 'desc': 'update_scrub_playout', 'params': {}})

        print('time check 7: {t}'.format(t=(time.time_ns() - ot) / 1000000))

        # Should probably just combine this with the scrub playout above
        event_queue.g_event_queue.push_msg({'what': 2, 'desc': 'update_playout_x_scroll', 'params': {'play_time': self.play_time}})


        print('time check 8: {t}'.format(t=(time.time_ns() - ot) / 1000000))


    def finished(self):
        if self.play_finished_cb is not None:
            self.play_finished_cb()

        event_queue.g_event_queue.push_msg({'what': 4, 'desc': 'update_notes_finished_playing', 'params': {'slots': self.last_played.copy()}})
        self.last_played.clear()

        dpg.configure_item(self.scrub_slots[self.play_time - 1], fill=[255, 255, 255, 255])
        dpg.configure_item(self.scrub_slots[self.play_time_start], fill=[255, 0, 0, 255])

    def play(self, finished_cb):
        self.stop()

        self.sample_manager = SampleManager()
        self.sample_manager.start()

        self.play_finished_cb = finished_cb
        self.play_time = self.play_time_start - 1   # -1 so that we 'start' and tick to the real start time
        self.play_thread = PlayThread()
        self.play_thread.start(self.tick, self.finished)

    def finish(self):
        if self.play_thread is not None:
            self.play_thread.kill()
            self.play_thread = None

        if self.sample_manager is not None:
            self.sample_manager.kill()
            self.sample_manager = None

    def stop(self):
        if self.play_thread is not None:
            self.play_thread.kill()
            self.play_thread.join()
            self.play_thread = None

        if self.sample_manager is not None:
            self.sample_manager.kill()
            self.sample_manager.join()
            self.sample_manager = None



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

            if g_play_stats.sounds_enabled:
                threading.Thread(target=SampleManager.play_sample, args=(sample['note'], sample['octave'],), daemon=True).start()
            # threading.Thread(target=SampleManager.play_input, args=(sample['key'],), daemon=True).start()
            pydirectinput.press(sample['key'])
            self.sample_queue.task_done()

    @staticmethod
    def play_input(key):
        print('play_input: ' + key)
        pydirectinput.press(key)

    @staticmethod
    def play_sample(note, oct):
        # Always play the same notes for the different samples -- the important thing is that we have a translation of 'sample' to 'index' as we really only have 3 for our playback
        octave = gwidi_data.g_measure_info.selected_octaves.index(oct)
        print('playing sample: {n} {o} -- real: {o2}'.format(n=note, o=oct, o2=octave))

        if note == 'C2':
            if octave == 0:
                playsound(g_play_stats.samples_dir + '/piano/c7.mp3')
            elif octave == 1:
                playsound(g_play_stats.samples_dir + '/piano/c6.mp3')
            elif octave == 2:
                playsound(g_play_stats.samples_dir + '/piano/c5.mp3')
        elif note == 'B':
            if octave == 0:
                playsound(g_play_stats.samples_dir + '/piano/b6.mp3')
            elif octave == 1:
                playsound(g_play_stats.samples_dir + '/piano/b5.mp3')
            elif octave == 2:
                playsound(g_play_stats.samples_dir + '/piano/b4.mp3')
        elif note == 'A':
            if octave == 0:
                playsound(g_play_stats.samples_dir + '/piano/a6.mp3')
            elif octave == 1:
                playsound(g_play_stats.samples_dir + '/piano/a5.mp3')
            elif octave == 2:
                playsound(g_play_stats.samples_dir + '/piano/a4.mp3')
        elif note == 'G':
            if octave == 0:
                playsound(g_play_stats.samples_dir + '/piano/g6.mp3')
            elif octave == 1:
                playsound(g_play_stats.samples_dir + '/piano/g5.mp3')
            elif octave == 2:
                playsound(g_play_stats.samples_dir + '/piano/g4.mp3')
        elif note == 'F':
            if octave == 0:
                playsound(g_play_stats.samples_dir + '/piano/f6.mp3')
            elif octave == 1:
                playsound(g_play_stats.samples_dir + '/piano/f5.mp3')
            elif octave == 2:
                playsound(g_play_stats.samples_dir + '/piano/f4.mp3')
        elif note == 'E':
            if octave == 0:
                playsound(g_play_stats.samples_dir + '/piano/e6.mp3')
            elif octave == 1:
                playsound(g_play_stats.samples_dir + '/piano/e5.mp3')
            elif octave == 2:
                playsound(g_play_stats.samples_dir + '/piano/e4.mp3')
        elif note == 'D':
            if octave == 0:
                playsound(g_play_stats.samples_dir + '/piano/d6.mp3')
            elif octave == 1:
                playsound(g_play_stats.samples_dir + '/piano/d5.mp3')
            elif octave == 2:
                playsound(g_play_stats.samples_dir + '/piano/d4.mp3')
        elif note == 'C1':
            if octave == 0:
                playsound(g_play_stats.samples_dir + '/piano/c6.mp3')
            elif octave == 1:
                playsound(g_play_stats.samples_dir + '/piano/c5.mp3')
            elif octave == 2:
                playsound(g_play_stats.samples_dir + '/piano/c4.mp3')


g_play_manager = None
g_play_stats = None
def init_play_manager():
    global g_play_manager
    global g_play_stats
    global g_sample_manager
    if g_play_manager is None:
        g_play_manager = PlayManager()

    if g_play_stats is None:
        g_play_stats = PlayStats()
