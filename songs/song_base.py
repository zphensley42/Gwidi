from abc import abstractmethod
from enum import Enum
import time



def FullNoteLength(bpm):
    return 240 / bpm

def HalfNoteLength(bpm):
    return 120 / bpm

def QuarterNoteLength(bpm):
    return 60 / bpm

def EighthNoteLength(bpm):
    return 30 / bpm

def SixteenthNoteLength(bpm):
    return 15 / bpm


class NoteLength(Enum):
    FULL = 1
    HALF = 2
    QUARTER = 3
    EIGHT = 4
    SIXTEENTH = 5
    STUCCATO = 6


class NoteType(Enum):
    E1 = 1
    FSHARP = 2
    GSHARP = 3
    A = 4
    B = 5
    CSHARP = 6
    DSHARP = 7
    E2 = 8
    SILENCE = 0
    WAIT = 9
    OCTAVE_CHANGE = 10
    STRAFE_STOP = 11

    HARP_C1 = 1
    HARP_D = 2
    HARP_E = 3
    HARP_F = 4
    HARP_G = 5
    HARP_A = 6
    HARP_B = 7
    HARP_C2 = 8


class Note:
    length: NoteLength.FULL
    note_type = NoteType.E1
    octave = 1
    is_tongued = False

    def __init__(self, le, nt, o, ton):
        self.length = le
        self.note_type = nt
        self.octave = o
        self.is_tongued = ton

    def sleep(self, bpm):
        if self.length == NoteLength.FULL:
            time.sleep(FullNoteLength(bpm))
        if self.length == NoteLength.HALF:
            time.sleep(HalfNoteLength(bpm))
        if self.length == NoteLength.QUARTER:
            time.sleep(QuarterNoteLength(bpm))
        if self.length == NoteLength.EIGHT:
            time.sleep(EighthNoteLength(bpm))
        if self.length == NoteLength.SIXTEENTH:
            time.sleep(SixteenthNoteLength(bpm))


class Song:
    bpm: 100

    @abstractmethod
    def notes(self):
        pass
