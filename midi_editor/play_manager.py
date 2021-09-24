import dearpygui.dearpygui as dpg

class PlayManager:
    def __init__(self):
        self.play_time = 0
        self.scrub_slots = []

    def scrub(self, play_time):
        self.play_time = play_time
        for s_iter, s in enumerate(self.scrub_slots):
            selected = s_iter == self.play_time
            fill = [255, 0, 0, 255] if selected else [255, 255, 255, 255]
            dpg.configure_item(s, fill=fill)


g_play_manager = None
def init_play_manager():
    global g_play_manager
    if g_play_manager is None:
        g_play_manager = PlayManager()