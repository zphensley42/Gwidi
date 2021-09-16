import keyboard
import pydirectinput
import time
import threading
from abc import abstractmethod


# TODO IDEA: On ALT press, begin suppressing keys as a 'trigger' for more hot keys
# i.e.:  hold alt, press q w e, release alt
# when holding alt, q w & e are suppressed from the system and only triggered in this script
# when releasing, things go back to normal


cbs = {}


def add_cb(key, cb):
    cbs[key] = cb


def get_cb(key):
    return cbs[key]


class DelayThread(threading.Thread):
    is_alive = False
    msg_queue = []
    msgs_to_perform = []
    msg_cv = threading.Condition()

    def post_msg(self, m):
        with self.msg_cv:
            self.msg_queue.append(m)
            self.msg_cv.notify()

    def remove_msg(self, name):
        for m in self.msg_queue:
            if m.name == name:
                self.msg_queue.remove(m)
                return

    def start(self):
        self.is_alive = True
        super().start()

    def stop(self):
        self.is_alive = False
        super().join()

    def run(self):
        while self.is_alive:
            while len(self.msg_queue) <= 0:
                with self.msg_cv:
                   self.msg_cv.wait()
                msg = self.msg_queue.pop(0)
                self.msgs_to_perform.append(msg)

            # perform based on msg
            for m in self.msgs_to_perform:
                if time.time_ns() >= msg.time:
                    print('performing: ' + m.name)
                    self.msgs_to_perform.remove(m)
                    m.perform()


delayThread = DelayThread()


# Necro Sword
def macro_2_worker():
    time.sleep(0.25)
    pydirectinput.press('5')
    time.sleep(2)
    pydirectinput.press('3')
    time.sleep(1.25)
    pydirectinput.press('4')
    time.sleep(1.5)
    pydirectinput.press('2')
    time.sleep(1.5)
    pydirectinput.press('`')
    time.sleep(0.25)
    pydirectinput.press('2')
    time.sleep(2)
    pydirectinput.press('5')
def macro_2():
    keyboard.call_later(macro_2_worker)


def macro_p():
    get_cb("p")()


press_times = {}
double_press_delay = 500 * 1000000  # 500 ms (in nanoseconds)
def detect_double_press_macro(key, real_cb):
    if key not in press_times:
        press_times[key] = time.time_ns()
        return

    now = time.time_ns()
    duration = now - press_times[key]
    if duration <= double_press_delay:
        real_cb()
        press_times.pop(key)
        return

    press_times[key] = time.time_ns()


class SlidingWindow:
    actions = []
    max_size = 10
    delay = 1000 * 1000000

    def last_action(self):
        if len(self.actions) <= 0:
            return None
        return self.actions[-1]

    def push(self, action):
        new_action = {
            "action": action,
            "expire": time.time_ns() + self.delay
        }
        self.actions.append(new_action)
        if len(self.actions) > self.max_size:
            self.actions.pop(0)

    def clear(self):
        self.actions.clear()

class Pattern:
    def matches(self, w):
        i, j = 0, 0
        while i < len(w.actions) and j < len(self.actions):
            if w.actions[i]['expire'] <= time.time_ns():
                i += 1
                continue

            if w.actions[i]['action'] == self.actions[j]:
                j += 1
            i += 1

        return j == len(self.actions)

    @abstractmethod
    def new_key(self):
        pass

    is_hold = False

class MinionSpawnPattern(Pattern):
    actions = ["ctrl down", "alt down", "alt up", "alt down", "alt up"]

    is_hold = False

    def run(self):
        time.sleep(0.25)
        pydirectinput.press('6')
        time.sleep(1.75)
        pydirectinput.press('7')
        time.sleep(1.75)
        pydirectinput.press('8')
        time.sleep(1.75)
        pydirectinput.press('9')
        time.sleep(1.75)
        pydirectinput.press('0')
        time.sleep(1.5)

    def new_key(self):
        pass

class MinionAttackPattern(Pattern):
    actions = ["ctrl down", "alt down"]

    class DelayMsg:
        name = "MinionAttackPatternDelay"
        time = time.time_ns() + (2000 * 1000000)    # 2s in ns
        def perform(self):
            time.sleep(0.25)
            pydirectinput.press('7')
            time.sleep(1.75)
            pydirectinput.press('8')
            time.sleep(1.75)
            pydirectinput.press('0')
            time.sleep(1.5)

    is_hold = True

    def run(self):
        # Only perform if we are 'holding', i.e. no more keys come in for X time (including not alt up)
        delayThread.post_msg(MinionAttackPattern.DelayMsg())

    def new_key(self):
        delayThread.remove_msg(MinionAttackPattern.DelayMsg.name)
        pass


window = SlidingWindow()
patterns = [
    MinionSpawnPattern(),
    # MinionAttackPattern(),
]
def detect_double_sys_key_worker(evt):
    fmt = "{key} {type}"
    last_act = window.last_action()
    fmt = fmt.format(key=evt.name, type=evt.event_type)
    window.push(fmt)

    for pattern in patterns:
        if pattern.matches(window):
            window.clear()
            print('matched')
            pattern.run()
            break
def detect_double_sys_key(evt):
    keyboard.call_later(detect_double_sys_key_worker, args=(evt,))

def new_key_pass(evt):
    for pattern in patterns:
        pattern.new_key()

def setup_macros():
    # keyboard.add_hotkey('ctrl+2', macro_2)
    keyboard.add_hotkey('ctrl+p', macro_p)

    # keyboard.add_hotkey('q, q', suppress=True, callback=macro_2, trigger_on_release=True)
    # keyboard.hook(detect_double_sys_key, suppress=False)
    # keyboard.hook(new_key_pass, suppress=False)


def run():
    setup_macros()
    # delayThread.start()

