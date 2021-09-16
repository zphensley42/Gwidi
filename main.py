# coding=utf-8
# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import midi_editor
import music
from macros import key_macros
import keyboard
import pydirectinput

pydirectinput.PAUSE = 0


def doMain():
    key_macros.run()
    key_macros.add_cb("p", music.run)


def cb_1():
    pydirectinput.press('6')

def cb_2():
    pydirectinput.press('7')

def cb_3():
    pydirectinput.press('8')

def cb_4():
    pydirectinput.press('9')

def cb_5():
    pydirectinput.press('0')

def setup_base_macros():
    keyboard.add_hotkey(hotkey='alt+1', suppress=True, callback=cb_1)
    keyboard.add_hotkey(hotkey='alt+2', suppress=True, callback=cb_2)
    keyboard.add_hotkey(hotkey='alt+3', suppress=True, callback=cb_3)
    keyboard.add_hotkey(hotkey='alt+4', suppress=True, callback=cb_4)
    keyboard.add_hotkey(hotkey='alt+5', suppress=True, callback=cb_5)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # midi_editor.run_editor()
    midi_editor.draw_editor()
    # doMain()
    # setup_base_macros()
    keyboard.wait()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
