from songs.song_base import *

# TODO: Make a string parser to make this even easier, maybe of the format
# G#8 B8 D#8 C#4 D#4
# D#8 D#8
# etc
# 2 notes of the same in a row are automatically 'tongued'

class GatosSong(Song):
    bpm = 97

    def notes(self):
        return [
            # Note(NoteLength.SIXTEENTH, NoteType.OCTAVE_CHANGE, 2, False),

            Note(NoteLength.QUARTER, NoteType.DSHARP, 1, False),
            Note(NoteLength.SIXTEENTH, NoteType.STRAFE_STOP, 1, False),
            Note(NoteLength.SIXTEENTH, NoteType.CSHARP, 1, False),
            Note(NoteLength.SIXTEENTH, NoteType.STRAFE_STOP, 1, False),
            Note(NoteLength.SIXTEENTH, NoteType.A, 1, False),
            Note(NoteLength.SIXTEENTH, NoteType.STRAFE_STOP, 1, False),
            Note(NoteLength.SIXTEENTH, NoteType.CSHARP, 1, True),
            Note(NoteLength.SIXTEENTH, NoteType.STRAFE_STOP, 1, False),
            Note(NoteLength.SIXTEENTH, NoteType.CSHARP, 1, False),
            Note(NoteLength.SIXTEENTH, NoteType.STRAFE_STOP, 1, False),
            Note(NoteLength.SIXTEENTH, NoteType.DSHARP, 1, False),
            Note(NoteLength.SIXTEENTH, NoteType.STRAFE_STOP, 1, False),
            Note(NoteLength.SIXTEENTH, NoteType.CSHARP, 1, False),
            Note(NoteLength.SIXTEENTH, NoteType.STRAFE_STOP, 1, False),
            Note(NoteLength.SIXTEENTH, NoteType.DSHARP, 1, True),
            Note(NoteLength.QUARTER, NoteType.DSHARP, 1, False),
            Note(NoteLength.SIXTEENTH, NoteType.E2, 1, False),
            Note(NoteLength.SIXTEENTH, NoteType.DSHARP, 1, False),
            Note(NoteLength.SIXTEENTH, NoteType.CSHARP, 1, False),
            Note(NoteLength.SIXTEENTH, NoteType.STRAFE_STOP, 1, False),
            Note(NoteLength.SIXTEENTH, NoteType.A, 1, False),
            Note(NoteLength.SIXTEENTH, NoteType.STRAFE_STOP, 1, False),
            Note(NoteLength.SIXTEENTH, NoteType.CSHARP, 1, True),
            Note(NoteLength.SIXTEENTH, NoteType.STRAFE_STOP, 1, False),
            Note(NoteLength.SIXTEENTH, NoteType.CSHARP, 1, False),
            Note(NoteLength.SIXTEENTH, NoteType.STRAFE_STOP, 1, False),
            Note(NoteLength.SIXTEENTH, NoteType.A, 1, True),
            Note(NoteLength.SIXTEENTH, NoteType.STRAFE_STOP, 1, False),
            Note(NoteLength.SIXTEENTH, NoteType.A, 1, False),
            Note(NoteLength.SIXTEENTH, NoteType.STRAFE_STOP, 1, False),
            Note(NoteLength.SIXTEENTH, NoteType.DSHARP, 1, False),
            Note(NoteLength.QUARTER, NoteType.CSHARP, 1, False),
            Note(NoteLength.SIXTEENTH, NoteType.STRAFE_STOP, 1, False),
            Note(NoteLength.SIXTEENTH, NoteType.A, 1, False),
            Note(NoteLength.SIXTEENTH, NoteType.STRAFE_STOP, 1, False),
            Note(NoteLength.SIXTEENTH, NoteType.GSHARP, 1, False),
            Note(NoteLength.SIXTEENTH, NoteType.STRAFE_STOP, 1, False),
            Note(NoteLength.QUARTER, NoteType.A, 1, False),
            Note(NoteLength.SIXTEENTH, NoteType.STRAFE_STOP, 1, False),
            Note(NoteLength.SIXTEENTH, NoteType.GSHARP, 1, False),
            Note(NoteLength.SIXTEENTH, NoteType.STRAFE_STOP, 1, False),
            Note(NoteLength.SIXTEENTH, NoteType.A, 1, False),
            Note(NoteLength.SIXTEENTH, NoteType.STRAFE_STOP, 1, False),
            Note(NoteLength.SIXTEENTH, NoteType.CSHARP, 1, False),
            Note(NoteLength.SIXTEENTH, NoteType.STRAFE_STOP, 1, False),
            Note(NoteLength.SIXTEENTH, NoteType.DSHARP, 1, False),
            Note(NoteLength.SIXTEENTH, NoteType.STRAFE_STOP, 1, False),
            Note(NoteLength.SIXTEENTH, NoteType.E2, 1, False),
            Note(NoteLength.SIXTEENTH, NoteType.DSHARP, 1, False),
            Note(NoteLength.QUARTER, NoteType.CSHARP, 1, False),
            Note(NoteLength.HALF, NoteType.DSHARP, 1, False),

            #
            Note(NoteLength.EIGHT, NoteType.SILENCE, 1, False),
        ]
