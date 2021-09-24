import dearpygui.dearpygui as dpg

class MeasureInfo:
    slots_per_measure = 16
    measure_count = 3
    octaves = [8, 7, 6, 5, 4, 3, 2, 1, 0]
    selected_octaves = [4, 5, 6]

    @staticmethod
    def update_measure_count(cnt):
        diff = MeasureInfo.measure_count - cnt
        if diff < 0:
            # adding (old < new)
            for n in g_measure_info.notes:
                n.add_slots(abs(diff) * MeasureInfo.slots_per_measure)
        elif diff > 0:
            # adding (old < new)
            for n in g_measure_info.notes:
                n.remove_slots(abs(diff) * MeasureInfo.slots_per_measure)

        MeasureInfo.measure_count = cnt



    note_vals = [
        {'label': 'C2', 'key': '8'},
        {'label': 'B', 'key': '7'},
        {'label': 'A', 'key': '6'},
        {'label': 'G', 'key': '5'},
        {'label': 'F', 'key': '4'},
        {'label': 'E', 'key': '3'},
        {'label': 'D', 'key': '2'},
        {'label': 'C1', 'key': '1'},
    ]

    notes = []
    def __init__(self):
        self.fill()

    def fill(self):
        for o in MeasureInfo.octaves:
            for nv in MeasureInfo.note_vals:
                # each nv / octave is a row of slots, go in order of octave -> notes
                MeasureInfo.notes.append(Note(nv, o))


    def clear(self):
        MeasureInfo.notes.clear()
        self.fill()


# Each note can be used to fill a horizontal list of slots that are marked as activated / held etc
# Each note is drawn per its octave / value
class Note:
    def __init__(self, note, octave):
        self.note = note
        self.octave = octave
        self.slots = []

        total_slots = MeasureInfo.slots_per_measure * MeasureInfo.measure_count
        for i in range(total_slots):
            self.slots.append(Slot(self.note, self.octave))

    def add_slots(self, num):
        for i in range(num):
            self.slots.append(Slot(self.note, self.octave))

    def remove_slots(self, num):
        self.slots = self.slots[0:(-1 * num)]


class Slot:
    def __init__(self, note, octave):
        self.note = note
        self.octave = octave

        self.activated = False
        self.is_held = False
        self.change_trigger = False
        self.is_playing = False
        self.rect = None
        self.rect_text = None

    def play(self):
        self.is_playing = True
        self.refresh()

    def finished_playing(self):
        self.is_playing = False
        self.refresh()

    def drawn(self, rect, rect_text):
        self.rect = rect
        self.rect_text = rect_text

    def refresh(self):
        dpg.configure_item(self.rect, fill=self.fill(), color=self.color())

    def activate(self):
        if self.change_trigger:
            return
        if self.activated:
            self.hold()
            return

        self.activated = True
        self.is_held = False
        self.change_trigger = True
        self.refresh()

    def clear(self):
        if self.change_trigger:
            return
        self.activated = False
        self.is_held = False
        self.change_trigger = True
        self.refresh()

    def hold(self):
        if self.change_trigger:
            return
        if self.is_held:
            self.activate()
            return

        self.is_held = True
        self.activated = False
        self.change_trigger = True
        self.refresh()

    def change_finished(self):
        self.change_trigger = False

    def fill(self):
        if self.activated:
            return [0, 255, 0, 255]
        elif self.is_held:
            return [0, 255, 255, 255]
        else:
            if self.octave in g_measure_info.selected_octaves:
                return [255, 255, 255, 255]
            else:
                return [150, 150, 150, 255]

    def color(self):
        if self.is_playing:
            return [0, 0, 255, 255]
        else:
            return [0, 0, 0, 255]


g_measure_info = None
def init_gwidi_data():
    global g_measure_info
    if g_measure_info is None:
        g_measure_info = MeasureInfo()
