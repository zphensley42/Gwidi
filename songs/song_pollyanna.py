from songs.song_base import *

# TODO: Make a string parser to make this even easier, maybe of the format
# G#8 B8 D#8 C#4 D#4
# D#8 D#8
# etc
# 2 notes of the same in a row are automatically 'tongued'

class Pollyanna(Song):
    bpm = 120

    def notes(self):
        return [
            Note(NoteLength.EIGHT, NoteType.GSHARP, 1, False),
            Note(NoteLength.EIGHT, NoteType.B, 1, False),
            Note(NoteLength.EIGHT, NoteType.DSHARP, 1, False),
            Note(NoteLength.QUARTER, NoteType.CSHARP, 1, False),
            Note(NoteLength.QUARTER, NoteType.DSHARP, 1, True),
            Note(NoteLength.EIGHT, NoteType.DSHARP, 1, True),
            Note(NoteLength.EIGHT, NoteType.DSHARP, 1, False),
            Note(NoteLength.QUARTER, NoteType.A, 1, False),
            Note(NoteLength.HALF, NoteType.B, 1, False),
            Note(NoteLength.EIGHT, NoteType.GSHARP, 1, False),
            Note(NoteLength.EIGHT, NoteType.B, 1, False),
            Note(NoteLength.EIGHT, NoteType.DSHARP, 1, False),
            Note(NoteLength.QUARTER, NoteType.CSHARP, 1, False),
            Note(NoteLength.QUARTER, NoteType.DSHARP, 1, True),
            Note(NoteLength.FULL, NoteType.DSHARP, 1, False),
            Note(NoteLength.EIGHT, NoteType.FSHARP, 1, True),
            Note(NoteLength.EIGHT, NoteType.FSHARP, 1, False),
            Note(NoteLength.EIGHT, NoteType.A, 1, True),
            Note(NoteLength.EIGHT, NoteType.A, 1, False),
            Note(NoteLength.QUARTER, NoteType.E2, 1, False),
            Note(NoteLength.EIGHT, NoteType.CSHARP, 1, False),
            Note(NoteLength.FULL, NoteType.DSHARP, 1, False),
            Note(NoteLength.EIGHT, NoteType.B, 1, True),
            Note(NoteLength.EIGHT, NoteType.B, 1, False),
            Note(NoteLength.EIGHT, NoteType.DSHARP, 1, True),
            Note(NoteLength.EIGHT, NoteType.DSHARP, 1, False),
            Note(NoteLength.SIXTEENTH, NoteType.OCTAVE_CHANGE, 0, False),
            Note(NoteLength.QUARTER, NoteType.FSHARP, 2, False),
            Note(NoteLength.SIXTEENTH, NoteType.OCTAVE_CHANGE, 0, False),
            Note(NoteLength.EIGHT, NoteType.DSHARP, 1, False),
            Note(NoteLength.HALF, NoteType.A, 1, False),
            Note(NoteLength.EIGHT, NoteType.GSHARP, 1, True),
            Note(NoteLength.HALF, NoteType.GSHARP, 1, False),
            Note(NoteLength.EIGHT, NoteType.FSHARP, 1, False),
            Note(NoteLength.EIGHT, NoteType.FSHARP, 1, False),
            Note(NoteLength.EIGHT, NoteType.A, 1, True),
            Note(NoteLength.EIGHT, NoteType.A, 1, False),
            Note(NoteLength.QUARTER, NoteType.E2, 1, False),
            Note(NoteLength.EIGHT, NoteType.CSHARP, 1, False),
            Note(NoteLength.FULL, NoteType.DSHARP, 1, False),
            Note(NoteLength.QUARTER, NoteType.A, 1, False),
            Note(NoteLength.EIGHT, NoteType.B, 1, True),
            Note(NoteLength.EIGHT, NoteType.B, 1, False),
            Note(NoteLength.EIGHT, NoteType.DSHARP, 1, True),
            Note(NoteLength.EIGHT, NoteType.DSHARP, 1, False),
            Note(NoteLength.SIXTEENTH, NoteType.OCTAVE_CHANGE, 0, False),
            Note(NoteLength.QUARTER, NoteType.FSHARP, 2, False),
            Note(NoteLength.SIXTEENTH, NoteType.OCTAVE_CHANGE, 0, False),
            Note(NoteLength.EIGHT, NoteType.DSHARP, 1, False),
            Note(NoteLength.HALF, NoteType.A, 1, False),
            Note(NoteLength.EIGHT, NoteType.GSHARP, 1, True),
            Note(NoteLength.HALF, NoteType.GSHARP, 1, False),

            Note(NoteLength.EIGHT, NoteType.GSHARP, 1, False),
            Note(NoteLength.EIGHT, NoteType.FSHARP, 1, False),
            Note(NoteLength.EIGHT, NoteType.E1, 1, False),
            Note(NoteLength.EIGHT, NoteType.FSHARP, 1, False),
            Note(NoteLength.QUARTER, NoteType.GSHARP, 1, False),
            Note(NoteLength.QUARTER, NoteType.CSHARP, 1, False),
            Note(NoteLength.QUARTER, NoteType.DSHARP, 1, False),

            Note(NoteLength.SIXTEENTH, NoteType.OCTAVE_CHANGE, 0, False),
            Note(NoteLength.QUARTER, NoteType.GSHARP, 2, False),
            Note(NoteLength.HALF, NoteType.CSHARP, 2, False),
            Note(NoteLength.SIXTEENTH, NoteType.OCTAVE_CHANGE, 0, False),

            Note(NoteLength.EIGHT, NoteType.DSHARP, 1, False),
            Note(NoteLength.EIGHT, NoteType.CSHARP, 1, False),
            Note(NoteLength.EIGHT, NoteType.B, 1, False),
            Note(NoteLength.EIGHT, NoteType.CSHARP, 1, False),
            Note(NoteLength.EIGHT, NoteType.DSHARP, 1, False),
            Note(NoteLength.EIGHT, NoteType.CSHARP, 1, False),
            Note(NoteLength.EIGHT, NoteType.B, 1, False),
            Note(NoteLength.EIGHT, NoteType.CSHARP, 1, False),
            Note(NoteLength.FULL, NoteType.DSHARP, 1, False),

            Note(NoteLength.EIGHT, NoteType.SILENCE, 1, False),
        ]
