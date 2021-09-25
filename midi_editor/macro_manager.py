import json
import keyboard
from dearpygui import dearpygui as dpg
import play_manager

class Utility:
    file_cb = None
    play_stop_cb = None

    special_chars = [
        {'val': 17, 'key': 'Ctrl'},
        {'val': 18, 'key': 'Alt'},
        {'val': 16, 'key': 'Shift'},
        {'val': 9, 'key': 'Tab'},
        {'val': 91, 'key': 'Winkey'},
        {'val': 219, 'key': '['},
        {'val': 221, 'key': ']'},
        {'val': 186, 'key': ';'},
        {'val': 222, 'key': '\''},
        {'val': 188, 'key': ','},
        {'val': 190, 'key': '.'},
        {'val': 191, 'key': '/'},
        {'val': 220, 'key': '\\'},
        {'val': 189, 'key': '-'},
        {'val': 187, 'key': '='},
        {'val': 8, 'key': 'Backspace'},
        {'val': 192, 'key': '`'},
        {'val': 37, 'key': 'Left Arrow'},
        {'val': 40, 'key': 'Down Arrow'},
        {'val': 39, 'key': 'Right Arrow'},
        {'val': 38, 'key': 'Up Arrow'},
        {'val': 32, 'key': 'Space'},
        {'val': 20, 'key': 'Caps Lock'},
        {'val': 13, 'key': 'Enter'},
    ]

    @staticmethod
    def key_to_str(key):
        entry = None
        for sk in Utility.special_chars:
            if sk['val'] == key:
                entry = sk
                break
        if entry is None:
            return chr(key)
        else:
            return entry['key']

    @staticmethod
    def macro_action_play_stop():
        print('macro_action_play_stop')
        # TODO: call callback to owner
        if Utility.play_stop_cb is not None:
            Utility.play_stop_cb()

    @staticmethod
    def macro_action_load_file(param):
        print('macro_action_load_file: {p}'.format(p=param))
        # TODO: call callback to owner
        if Utility.file_cb is not None:
            Utility.file_cb(param)

    assigned_macros = []

    @staticmethod
    def assign_macros():
        # clear / assign macros
        Utility.clear_macros()
        for m in MacroManager.prefs.macros:
            Utility.assign_macro(m)

    @staticmethod
    def clear_macros():
        print('clearing macros')

        for m in Utility.assigned_macros:
            keyboard.remove_hotkey(m)

        Utility.assigned_macros.clear()

    @staticmethod
    def assign_macro(m):
        key_string = ''
        for iter, k in enumerate(m['val']):
            if iter > 0:
                key_string += '+'
            key_string += Utility.key_to_str(k).lower()

        action = m['action']
        if action not in Preferences.action_types:
            print('Invalid action supplied: {m}'.format(m=m))
        else:
            print('assigning macro: {m}, keys: {k}'.format(m=m, k=key_string))
            if action == 'play_stop':
                handler = keyboard.add_hotkey(key_string, Utility.macro_action_play_stop, suppress=True,
                                              trigger_on_release=True)
                Utility.assigned_macros.append(handler)
            elif action == 'load_file':
                handler = keyboard.add_hotkey(key_string, lambda: Utility.macro_action_load_file(m['param']), suppress=True,
                                              trigger_on_release=True)
                Utility.assigned_macros.append(handler)


class Preferences:
    action_types = [
        'play_stop',
        'load_file'
    ]

    def __init__(self):
        self.macros = [
            {'macro': 'Play / Stop', 'val': None, 'param': None, 'param_enabled': False, 'action': 'play_stop'},
            {'macro': 'Load File 1', 'val': None, 'param': '<file>', 'param_enabled': True, 'action': 'load_file'},
        ]

        self.load()

    def save(self):
        out = open('prefs.json', mode='w')
        out.write(json.dumps(self.macros))

    def load(self):
        input = open('prefs.json', mode='r')
        in_str = input.read()
        if len(in_str) > 0:
            obj = json.loads(in_str)
            self.macros = obj



class UIMacro:
    # Purpose is to update the 'param' property of preference with whatever is input on the 'dialog'
    def update_param(self, sender, data):
        print('update_param data={d}'.format(d=data))
        dpg.set_item_user_data(sender, data)

    def save_param(self, new_param):
        self.preference['param'] = new_param
        self.close_input(False)

    def show_param_input(self):
        px = (dpg.get_viewport_width() - 200) / 2
        py = (dpg.get_viewport_height() - 100) / 2

        with dpg.window(id='param_key_input_window', popup=True, modal=True, label='Param Input', width=200, height=100, pos=[px, py],
                        no_close=True, no_resize=False, no_move=False) as w:

            t = dpg.add_input_text(default_value=self.preference['param'], pos=[20, 100 / 2 - 10], callback=self.update_param)
            dpg.add_button(label="OK", width=50, pos=[20, 100 - 30], callback=lambda: self.save_param(dpg.get_item_user_data(t)))
            dpg.add_button(label="Cancel", width=50, pos=[200 - 20 - 50, 100 - 30],
                           callback=lambda: self.save_param(self.preference['param']))


    # Purpose is to update the 'val' property of preference with whatever is input on the 'dialog'
    def update_keys(self, new_keys, data, text):
        key = data[0]
        if key not in new_keys:
            new_keys.append(key)

        s = ''
        for iter, k in enumerate(new_keys):
            if iter > 0:
                s += '+'
            s += Utility.key_to_str(k)

        dpg.configure_item(text, default_value=s)

    def save_keys(self, new_keys):
        self.preference['val'] = new_keys

        self.close_input(True)

    def show_key_input(self):
        kdl = None
        px = (dpg.get_viewport_width() - 200) / 2
        py = (dpg.get_viewport_height() - 100) / 2

        new_keys = []

        with dpg.window(id='param_key_input_window', popup=True, modal=True, label='Key Input', width=200, height=100, pos=[px, py], no_close=True, no_resize=True, no_move=True, on_close=lambda: {
            # Clean up the listener on close
            dpg.delete_item(kdl)
        }) as w:
            t = dpg.add_text(default_value='<>', pos=[20, 100 / 2 - 10])
            dpg.add_button(label="OK", width=50, pos=[20, 100 - 30], callback=lambda: self.save_keys(new_keys))
            dpg.add_button(label="Cancel", width=50, pos=[200 - 20 - 50, 100 - 30], callback=lambda: self.save_keys(self.preference['val']))

            with dpg.handler_registry(id="bi_registry"):
                kdl = dpg.add_key_down_handler(callback=lambda s, d: self.update_keys(new_keys, d, t))

    def close_input(self, do_delete_registry):
        print('close_key_input trace')

        dpg.delete_item('param_key_input_window')
        if do_delete_registry:
            dpg.delete_item(item="bi_registry")

        MacroManager.prefs.save()
        MacroManager.show_macros(Utility.play_stop_cb, Utility.file_cb)


    # action -> lambda to call on macro usage (i.e. when it is activated)
    def __init__(self, action, preference):
        self.action = action
        self.preference = preference

        key_str = ''
        if self.preference['val'] is not None:
            for iter, v in enumerate(self.preference['val']):
                if iter > 0:
                    key_str += '+'
                key_str += Utility.key_to_str(v)
        else:
            key_str = '< >'
        self.key = key_str

    def draw(self, parent):
        dpg.add_text(parent=parent, default_value=self.preference['macro'])
        dpg.add_table_next_column(parent=parent)

        dpg.add_button(parent=parent, label=self.key, callback=self.show_key_input)
        dpg.add_table_next_column(parent=parent)

        dpg.add_button(parent=parent, label=self.preference['param'], callback=self.show_param_input, show=self.preference['param_enabled'])
        dpg.add_table_next_column(parent=parent)

class MacroManager:
    prefs = Preferences()

    @staticmethod
    def add_file_macro():
        f_macro_num = len(MacroManager.prefs.macros)
        new_m = {
            'macro': 'Load File {n}'.format(n=f_macro_num), 'val': [], 'param': '<file>', 'param_enabled': True, 'action': 'load_file'
        }
        MacroManager.prefs.macros.append(new_m)
        MacroManager.refresh_macros()

    @staticmethod
    def refresh_macros():
        if dpg.does_item_exist('macro_table'):
            dpg.delete_item('macro_table')
        if dpg.does_item_exist('add_macro_button'):
            dpg.delete_item('add_macro_button')
        if dpg.does_item_exist('save_macros_button'):
            dpg.delete_item('save_macros_button')

        dpg.add_table(id='macro_table', parent='configure_macros_window', header_row=True)
        dpg.add_table_column(parent='macro_table', label='Action')
        dpg.add_table_column(parent='macro_table', label='Key')
        dpg.add_table_column(parent='macro_table', label='Param')

        for m in MacroManager.prefs.macros:
            ui_mac = UIMacro(lambda: print('macro action'), m)
            ui_mac.draw('macro_table')

        dpg.add_button(id='add_macro_button', parent='configure_macros_window', label="Add File Macro", callback=MacroManager.add_file_macro)
        dpg.add_button(id='save_macros_button', parent='configure_macros_window', label="Save Macros", callback=MacroManager.save_macros)


    @staticmethod
    def show_macros(play_stop_cb, file_cb):
        Utility.play_stop_cb = play_stop_cb
        Utility.file_cb = file_cb
        h = 400
        w = 400
        px = (dpg.get_viewport_width() - w) / 2
        py = (dpg.get_viewport_height() - h) / 2
        dpg.add_window(id='configure_macros_window', label='Configure Macros', width=w, height=400, pos=[px, py], modal=True, popup=True, on_close=lambda: MacroManager.hide_macros())

        Utility.clear_macros()  # Ensure we don't suppress while assigning macros
        MacroManager.prefs.load()
        MacroManager.refresh_macros()

    @staticmethod
    def save_macros():
        MacroManager.prefs.save()
        Utility.assign_macros()
        MacroManager.hide_macros()

    @staticmethod
    def hide_macros():
        dpg.delete_item('macro_table')
        dpg.delete_item('add_macro_button')
        dpg.delete_item('save_macros_button')
        dpg.delete_item('configure_macros_window')

    @staticmethod
    def update_macro_pref(d, text, new_keys):
        if d[0] not in new_keys:
            new_keys.append(d[0])

        t_str = ''
        for iter, d in enumerate(new_keys):
            if iter > 0:
                t_str += '+'
            t_str += Utility.key_to_str(d)
        dpg.configure_item(text, default_value=t_str)



def res_cb(sender, data):
    dpg.configure_item('configure_macros_window', width=dpg.get_viewport_width(), height=dpg.get_viewport_height())




def on_play_stop_action():
    print('play_stop action called')

def on_file_action(param):
    print('file action called')

if __name__ == '__main__':
    dpg.add_window(label='test_importer', id='test_importer_id')

    dpg.setup_viewport()
    dpg.set_viewport_width(900)
    dpg.set_viewport_width(600)
    dpg.set_viewport_resize_callback(res_cb)
    dpg.set_primary_window(window="test_importer_id", value=True)

    MacroManager.show_macros(on_play_stop_action, on_file_action)

    # res_cb(0, {})
    dpg.start_dearpygui()

