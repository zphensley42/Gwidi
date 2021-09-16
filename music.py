import pyautogui
import pydirectinput
import time
from songs.song_pollyanna import Pollyanna
from songs.song_ff_fanfare import FFFanfare
from songs.song_gatos_song import GatosSong
from songs.song_base import NoteType

BPM = 117
FullNoteLength = 240 / BPM
HalfNoteLength = 120 / BPM
QuarterNoteLength = 60 / BPM	# quarter note gets the beat
EighthNoteLength = 30 / BPM
SixteenthNoteLength = 15 / BPM

note_e1 = 1
note_fsharp = 2
note_gsharp = 3
note_a = 4
note_b = 5
note_csharp = 6
note_dsharp = 7
note_e2 = 8

pydirectinput.PAUSE = 0

class Song:
    notes = []
    def play(self):
        pyautogui.alert('Empty song selected!')


def octave_change():
    pydirectinput.press('9')
    time.sleep(0.005)


def play_note(note):
    if note == '11':
        pydirectinput.press('w')
        # time.sleep(0.000001)
        # pydirectinput.keyUp('w')
    else:
        pydirectinput.press('' + note)


def choose_song():
    # song = pyautogui.prompt("Which song do you wish to play?")
    # print("You chose: " + song)
    # time.sleep(1)

    toPlay = Pollyanna()
    # toPlay = FFFanfare()
    # toPlay = GatosSong()
    for note in toPlay.notes():
        if note.note_type == NoteType.OCTAVE_CHANGE:
            octave_change()
            continue

        if note.note_type != NoteType.WAIT:
            play_note(str(note.note_type.value))
        note.sleep(toPlay.bpm)

        if note.is_tongued:
            pydirectinput.keyDown('a', _pause=False)
            pydirectinput.press('1', _pause=False)
            time.sleep(0.0001)
            pydirectinput.keyUp('a', _pause=False)
            pydirectinput.keyUp('1', _pause=False)
        # pydirectinput.press('w')
        # time.sleep(0.01)



def run():
    choose_song()

1