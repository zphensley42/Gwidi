import dearpygui.dearpygui as dpg

class MeasureInfo:
    slots_per_measure = 16
    measure_count = 3
    octaves = [2, 1, 0]

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
        for o in MeasureInfo.octaves:
            for nv in MeasureInfo.note_vals:
                # each nv / octave is a row of slots, go in order of octave -> notes
                MeasureInfo.notes.append(Note(nv, o))


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
            return [255, 255, 255, 255]

    def color(self):
        if self.is_playing:
            return [0, 0, 255, 0]
        else:
            return [255, 255, 255, 255]


g_measure_info = None
def init_gwidi_data():
    global g_measure_info
    if g_measure_info is None:
        g_measure_info = MeasureInfo()
