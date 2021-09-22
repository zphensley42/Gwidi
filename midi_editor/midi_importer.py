from mido import MidiFile, second2tick
import dearpygui.dearpygui as dpg
from inspect import currentframe, getframeinfo
from inspect import currentframe, stack

# https://www.twilio.com/blog/working-with-midi-data-in-python-using-mido
# http://www.music.mcgill.ca/~ich/classes/mumt306/StandardMIDIfileformat.html


# TODO: Better format all of this to be properly encompassed in the module

class NoteNumberTable:
    notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    @staticmethod
    def convert_to_note_repr(index):
        # min = 0, max = 127
        if index < 0:
            index = 0
        elif index > 127:
            index = 127

        # 12 notes (C C# D D# E F F# G G# A A# B)

        octave = int((index / 12))
        note = index % 12
        return {'note': NoteNumberTable.notes[note], 'octave': octave}

note_numbers = [
    {'num': 0, 'note': 'C', 'octave': -1},
    {'num': 0, 'note': 'C', 'octave': -1},
]


def line_stats():
    cf = currentframe()
    filename = getframeinfo(cf).filename
    return "{f}:{l}".format(f=filename, l=cf.f_back.f_back.f_lineno)  # 2 frames back b/c of log()

# Utility
def log(m):
    print("{s} {m}".format(s=line_stats(), m=m))

def tempo_to_bpm(t):
    return 60000000 / t


class NoteObj:
    def __init__(self, note):
        self.note = note
        self.on = None
        self.off = None

    # in 16th-notes
    def length(self):
        if self.off is None or self.on is None:
            return -1
        return abs(self.off - self.on)

    def start(self):
        return self.on

    def __repr__(self):
        return "{{note: {n}, start: {s}, length: {l}, on: {o}, off: {f}}}".format(n=self.note, s=self.start(), l=self.length(), o=self.on, f=self.off)

class Note:
    ticks_per_beat = 384
    # note_16 = ticks_per_beat / 4
    # note_8 = ticks_per_beat / 2
    # note_4 = ticks_per_beat
    # note_2 = ticks_per_beat * 2
    # note_1 = ticks_per_beat * 4
    note_lengths = [
        {"type": "none", "val": 0},
        {"type": "silence", "val": 0},
        {"type": "note_1", "val": int(ticks_per_beat * 4)},
        {"type": "note_2", "val": int(ticks_per_beat * 2)},
        {"type": "note_4", "val": int(ticks_per_beat * 1)},
        {"type": "note_8", "val": int(ticks_per_beat / 2)},
        {"type": "note_16", "val": int(ticks_per_beat / 4)},
    ]

    def __init__(self, n, c, on):
        global g_tempo
        self.note = n
        self.channel = c
        self.on_t = int(second2tick(on, Note.ticks_per_beat, g_tempo))
        self.off_t = 0
        self.is_completed = False

    def off_inc(self, time):
        self.off_t += int(second2tick(time, Note.ticks_per_beat, g_tempo))

    def complete(self):
        self.is_completed = True

    def completed(self):
        return self.is_completed

    def __eq__(self, other):
        return self.note == other.note and self.channel == other.channel

    def __repr__(self):
        return "{{note: {n}, channel: {c}, on: {o1}, off: {o2}, closest_note: {cl}, offset_note: {ofn}}}".format(n=self.note, c=self.channel, o1=self.on_t, o2=self.off_t, cl=self.closest_note_length(), ofn=self.offset_note())

    # returns how long of a 'silence' there is before this note's on
    def offset_note(self):
        if self.on_t == 0:
            return Note.note_lengths[0]
        else:
            nl = Note.note_lengths[1]
            n = self.closest_note_length_worker(self.on_t)
            copy = {"type": nl['type'], "val": n['val']}

            return copy

    def closest_note_length(self):
        return self.closest_note_length_worker(self.off_t)

    def closest_note_length_worker(self, off):
        cur_diff = None
        cur_note = None
        for nl in Note.note_lengths[2:]:
            new_diff = abs(nl['val'] - off)
            if cur_diff is None or cur_diff > new_diff:
                cur_diff = new_diff
                cur_note = nl

        return cur_note

class Utility:
    @staticmethod
    def note_count(notes, channel):
        filtered = filter(lambda note: note.channel == channel, notes)
        return len(list(filtered))

g_tempo = 60000000
g_table_children = []
g_table_children_x_off = 100
g_select_complete_cb = None
def select_data(sender, data):
    global g_select_complete_cb
    data = dpg.get_item_user_data(sender)
    g_select_complete_cb(data)
    dpg.delete_item(item="main_window")


def do_import(sender, data):
    global g_tempo
    global item_width
    global item_height
    global g_table_children_x_off
    global g_select_complete_cb

    log('do_import: {s} - {d}'.format(s=sender, d=data))

    imported = MidiFile(data['file_path_name'], clip=True)
    Note.ticks_per_beat = imported.ticks_per_beat
    log('imported midi file')
    bpm = 120
    for m in imported.tracks[0]:
        if m.type == 'set_tempo':
            g_tempo = m.tempo
            bpm = tempo_to_bpm(m.tempo)
            break

    log('detected bpm: {b}'.format(b=bpm))

    messages_in_order = []
    notes = []

    for iter, msg in enumerate(imported):
        if not msg.is_meta:
            messages_in_order.append(msg)

            # build up the delta times for each note not completed
            # if msg.type == 'note_on' or msg.type == 'note_off':
            for n in notes:
                if not n.completed():
                    n.off_inc(msg.time)

            if msg.type == 'note_on':
                notes.append(Note(msg.note, msg.channel, msg.time))
            elif msg.type == 'note_off':
                for n in notes:
                    if not n.completed() and n == msg:
                        n.complete()



    channels = []
    for n in notes:
        if n.channel not in channels:
            channels.append(n.channel)

    for c in channels:
        # build a table with the note info
        with dpg.child(parent="main_window", width=item_width - g_table_children_x_off, height=600, pos=[int(g_table_children_x_off / 2), 10 + ((600 + 20) * c)]) as tc:
            g_table_children.append(tc)
            dpg.add_text(default_value="Channel {n} -- note count: {nc}".format(n=c, nc=Utility.note_count(notes, c)))
            dpg.add_button(label="Use this channel", callback=select_data, user_data={'selected_channel': 2, 'data': notes})
            with dpg.table(header_row=True):
                dpg.add_table_column(label='Note')
                dpg.add_table_column(label='Channel')
                dpg.add_table_column(label='On')
                dpg.add_table_column(label='Off')
                dpg.add_table_column(label='Closest Note')
                dpg.add_table_column(label='Offset Note')

                for n in notes:
                    if n.channel != c:
                        continue

                    dpg.add_text(default_value=n.note)
                    dpg.add_table_next_column()

                    dpg.add_text(default_value=n.channel)
                    dpg.add_table_next_column()

                    dpg.add_text(default_value=n.on_t)
                    dpg.add_table_next_column()

                    dpg.add_text(default_value=n.off_t)
                    dpg.add_table_next_column()

                    dpg.add_text(default_value=str(n.closest_note_length()))
                    dpg.add_table_next_column()

                    dpg.add_text(default_value=str(n.offset_note()))
                    dpg.add_table_next_column()



vp_width = 900
vp_height = 600
def res_cb(sender, data):
    global vp_width
    global vp_height
    vp_width = dpg.get_viewport_width() - 50
    vp_height = dpg.get_viewport_height()

    dpg.configure_item(item="main_window", width=vp_width, height=vp_height)

    res_item_cb(sender, data)


item_width = 900
item_height = 600
def res_item_cb(sender, data):
    global item_width
    global item_height
    global g_table_children_x_off

    item_width = dpg.get_item_width("main_window") - g_table_children_x_off
    item_height = dpg.get_item_height("main_window")

    for tc in g_table_children:
        dpg.configure_item(tc, width=item_width)


def start_importer(fname, select_complete_cb):
    global g_select_complete_cb
    g_select_complete_cb = select_complete_cb

    with dpg.window(label="Gwidi MIDI Importer", id="main_window", modal=True, popup=True) as w:
        dpg.add_resize_handler(parent=w, callback=res_item_cb)

        log('importer started')
        do_import(None, {'file_path_name': fname})


def select_comp(data):
    print('select_comp({d})'.format(d=data))

if __name__ == '__main__':
    dpg.add_window(label='test_importer', id='test_importer_id')

    dpg.setup_viewport()
    dpg.set_viewport_width(900)
    dpg.set_viewport_width(600)
    dpg.set_viewport_resize_callback(res_cb)
    dpg.set_primary_window(window="test_importer_id", value=True)

    start_importer('../assets/midi_test/hm.mid', select_comp)

    res_cb(0, {})
    dpg.start_dearpygui()
