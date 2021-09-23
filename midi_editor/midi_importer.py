from mido import MidiFile, second2tick
import dearpygui.dearpygui as dpg
from inspect import currentframe, getframeinfo
from inspect import currentframe, stack

# https://www.twilio.com/blog/working-with-midi-data-in-python-using-mido
# http://www.music.mcgill.ca/~ich/classes/mumt306/StandardMIDIfileformat.html


# TODO: Better format all of this to be properly encompassed in the module

class NoteNumberTable:
    notes = ['C1', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
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


class LogUtil:
    @staticmethod
    def line_stats():
        cf = currentframe()
        filename = getframeinfo(cf).filename
        return "{f}:{l}".format(f=filename, l=cf.f_back.f_back.f_lineno)  # 2 frames back b/c of log()

    @staticmethod
    def log(m):
        print("{s} {m}".format(s=LogUtil.line_stats(), m=m))


class Utility:
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

    @staticmethod
    def tempo_to_bpm(t):
        return 60000000 / t

    @staticmethod
    def note_count(notes, channel):
        filtered = filter(lambda note: note.channel == channel, notes)
        return len(list(filtered))

    @staticmethod
    def note_length(length):
        cur_diff = None
        cur_note = None
        for nl in Utility.note_lengths[2:]:
            new_diff = abs(nl['val'] - length)
            if cur_diff is None or cur_diff > new_diff:
                cur_diff = new_diff
                cur_note = nl

        return cur_note



class Note:
    def __init__(self, n, c, on):
        self.note = n
        self.note_repr = NoteNumberTable.convert_to_note_repr(n)
        self.channel = c
        self.on_t = int(second2tick(on, Note.ticks_per_beat, MidiImporter.tempo))
        self.off_t = 0
        self.is_completed = False

    def off_inc(self, time):
        self.off_t += int(second2tick(time, Note.ticks_per_beat, MidiImporter.tempo))

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
            copy = {"type": nl['type'], "val": n['type']}

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

class MidiImporter:
    vp_width = 900
    vp_height = 600
    tempo = 60000000
    bpm = 120

    def __init__(self):
        self.table_children = []
        self.table_children_x_off = 100
        self.select_complete_cb = None
        self.item_width = 900
        self.item_height = 600

    def select_data(self, sender, data):
        data = dpg.get_item_user_data(sender)
        self.select_complete_cb(data)
        dpg.delete_item(item="importer_main_window")

    # TODO: Change this to build a list of stacks per note/octave combination, using a parsing cursor for current location -> visual repo below:
    # 'on' times > 0 mean ticks since the last note (not the last note in the stack), thus the parsing cursor is import for tracking the last position
    # note 50 [{position: 768, length: 96}]
    # note 55 [{position: 96, length: 192} {position: 384, length: 96}]
    # note 57 [{position: 0, length: 192} {position: 384, length: 96}]
    # note 59 [{position: 768, length: 96}]
    # TODO: Key is the cursor tracking where we are
    def do_import(self, sender, data):
        LogUtil.log('do_import: {s} - {d}'.format(s=sender, d=data))

        imported = MidiFile(data['file_path_name'], clip=True)
        Note.ticks_per_beat = imported.ticks_per_beat
        LogUtil.log('imported midi file')
        for m in imported.tracks[0]:
            if m.type == 'set_tempo':
                MidiImporter.tempo = m.tempo
                MidiImporter.bpm = Utility.tempo_to_bpm(m.tempo)
                break

        LogUtil.log('detected bpm: {b}'.format(b=MidiImporter.bpm))

        cursor = 0
        channels = {}
        for m in imported:
            if not m.is_meta and (m.type == 'note_on' or m.type == 'note_off'):
                # move to the beginning of the note
                cursor += second2tick(m.time, Note.ticks_per_beat, MidiImporter.tempo)

                if m.channel not in channels:
                    channels[m.channel] = {}
                notes = channels[m.channel]

                if m.note not in notes:
                    notes[m.note] = []
                note_positions = notes[m.note]

                # use on/off to determine when a position is complete and we should push a new one
                if m.type == 'note_on':
                    note_positions.append({
                        'repr': NoteNumberTable.convert_to_note_repr(m.note),
                        'position': cursor,
                        'length': 0,
                        'note_type': 'none'
                    })
                elif m.type == 'note_off':
                    np = note_positions[-1]
                    np['length'] = cursor - np['position']
                    np['note_type'] = Utility.note_length(np['length'])


        for k in channels.keys():
            # build a table with the note info
            with dpg.child(parent="main_window", width=self.item_width - self.table_children_x_off, height=600, pos=[int(self.table_children_x_off / 2), 10 + ((600 + 20) * k)]) as tc:
                self.table_children.append(tc)

                # move this to utility
                note_count = 0
                for n in channels[k]:
                    note_count += len(channels[k][n])

                dpg.add_text(default_value="Channel {n} -- note count: {nc}".format(n=k, nc=note_count))
                dpg.add_button(label="Use this channel", callback=self.select_data, user_data={'bpm': MidiImporter.bpm, 'selected_channel': k, 'data': channels[k]})
                with dpg.table(header_row=True):
                    dpg.add_table_column(label='Note')
                    dpg.add_table_column(label='Position')
                    dpg.add_table_column(label='Length')
                    # dpg.add_table_column(label='Closest Note')  # use 'note representation' to give note_16, note_8, etc
                    # dpg.add_table_column(label='Offset Note')

                    for n in channels[k]:
                        # note row
                        for p in channels[k][n]:
                            # note position
                            dpg.add_text(default_value=n)
                            dpg.add_table_next_column()

                            dpg.add_text(default_value=p['position'])
                            dpg.add_table_next_column()

                            dpg.add_text(default_value=p['length'])
                            dpg.add_table_next_column()

    def res_item_cb(self, sender, data):
        item_width = dpg.get_item_width("importer_main_window") - self.table_children_x_off
        item_height = dpg.get_item_height("importer_main_window")

        for tc in self.table_children:
            dpg.configure_item(tc, width=item_width)

    def start_importer(self, fname, select_complete_cb):
        self.select_complete_cb = select_complete_cb

        with dpg.window(label="Gwidi MIDI Importer", id="importer_main_window", modal=True, popup=True) as w:
            dpg.add_resize_handler(parent=w, callback=self.res_item_cb)

            LogUtil.log('importer started')
            self.do_import(None, {'file_path_name': fname})


def select_comp(data):
    print('select_comp({d})'.format(d=data))

importer = None
def show_importer(fname, cb, w, h):
    global importer
    importer = MidiImporter()
    importer.start_importer(fname, cb)

    refresh_importer(w, h)

def refresh_importer(w, h):
    MidiImporter.vp_width = w - 50
    MidiImporter.vp_height = h

    dpg.configure_item(item="importer_main_window", width=MidiImporter.vp_width, height=MidiImporter.vp_height)
    importer.res_item_cb(0, {})

def res_cb(sender, data):
    refresh_importer(dpg.get_viewport_width() - 50, dpg.get_viewport_height())

if __name__ == '__main__':
    dpg.add_window(label='test_importer', id='test_importer_id')

    dpg.setup_viewport()
    dpg.set_viewport_width(900)
    dpg.set_viewport_width(600)
    dpg.set_viewport_resize_callback(res_cb)
    dpg.set_primary_window(window="test_importer_id", value=True)

    show_importer('../assets/midi_test/test.mid', select_comp, 900, 600)

    res_cb(0, {})
    dpg.start_dearpygui()


# TODO: Importer needs to pick notes that we can actually support (close matches would have to be made i.e. flats / sharps to notes)