import dearpygui.dearpygui as dpg
import event_queue
import thread_pool

# messages
# {'what': 100, 'desc': 'data_assign_complete', 'params': {}}

class MeasuresDisplay:

    class MouseStats:
        def __init__(self, owner):
            self.owner = owner

            self.mouse_pos = None
            self.mouse_offset = None

            self.is_down = False
            self.active_button = -1

            if dpg.does_item_exist('md_mouse_registry'):
                dpg.delete_item('md_down_handler')
                dpg.delete_item('md_up_handler')
                dpg.delete_item('md_move_handler')
                dpg.delete_item('md_mouse_registry')

            with dpg.handler_registry(id='md_mouse_registry'):
                dpg.add_mouse_down_handler(id='md_down_handler', callback=owner.panel_mouse_down)
                dpg.add_mouse_release_handler(id='md_up_handler', callback=owner.panel_mouse_up)
                dpg.add_mouse_move_handler(id='md_move_handler', callback=owner.panel_mouse_moved)

        def trigger(self):
            if self.is_down:
                return False
            self.is_down = True

            # 0, 1, 2
            for i in range(2):
                if dpg.is_mouse_button_down(i):
                    self.active_button = i
                    break

            return True

        def clear(self):
            self.is_down = False
            self.active_button = -1

        def translate_pos_to_indices(self, boundaries):
            translated_pos = [
                self.mouse_pos[0] - self.mouse_offset[0] + dpg.get_x_scroll('md_panel'),
                self.mouse_pos[1] - self.mouse_offset[1] + dpg.get_y_scroll('md_panel'),
            ]

            # first, drill into the proper boundary
            found = None
            for b in boundaries:
                if b['x1'] <= translated_pos[0] <= b['x2'] and b['y1'] <= translated_pos[1] <= b['y2']:
                    found = b
                    break

            if found is None:
                return None

            # second, get the note / slot indices
            w_offset = translated_pos[0] - found['x1']
            h_offset = translated_pos[1] - found['y1']
            w_index = int(w_offset / MeasuresDisplay.slot_width)
            h_index = int(h_offset / MeasuresDisplay.slot_height)

            # finally convert to the total indices instead of per measure/octave
            slot_index = (found['measure'] * self.owner.slots_per_measure) + w_index
            note_index = (found['octave'] * self.owner.notes_per_octave) + h_index
            print('note_index: {n}, slot_index: {s}'.format(s=slot_index, n=note_index))
            return [note_index, slot_index]

    note_mapping = [
        'C2',
        'B',
        'A',
        'G',
        'F',
        'E',
        'D',
        'C1',
    ]

    class UiEventHandler(event_queue.Handler):
        def __init__(self, parent):
            self.parent = parent

        def handles(self, m_what):
            return m_what == 100

        def handle(self, msg):
            if msg['what'] == 100:
                self.parent.draw()

    slot_width = 50
    slot_height = 25
    measure_spacing = 10
    octave_spacing = 20
    slot_padding = 4

    def __init__(self, w, h, scrollbar_offset):
        self.width = w
        self.height = h
        self.slots_per_measure = 16
        self.notes_per_octave = 8
        self.num_octaves = 9
        self.num_measures = 3
        self.scrollbar_offset = scrollbar_offset
        self.measure_width = self.slots_per_measure * MeasuresDisplay.slot_width
        self.octave_height = self.notes_per_octave * MeasuresDisplay.slot_height

        self.measure_boundaries = []
        self.mouse_stats = MeasuresDisplay.MouseStats(self)

        cols = self.slots_per_measure * self.num_measures
        rows = self.notes_per_octave * self.num_octaves
        self.slots = [[0] * cols for i in range(rows)]

        self.ui_event_handler = MeasuresDisplay.UiEventHandler(self)
        event_queue.g_event_queue.subscribe(self.ui_event_handler)

    def assign_data_worker(self, data):
        # todo: fill in with real logic
        cols = self.slots_per_measure * self.num_measures
        rows = self.notes_per_octave * self.num_octaves
        self.slots = [[1] * cols for i in range(rows)]

        event_queue.g_event_queue.push_msg({'what': 100, 'desc': 'data_assign_complete', 'params': {}})

    def assign_data(self, data):
        thread_pool.push_async_task(lambda: self.assign_data_worker(data))

    # TODO: Setup mouse controls
    def panel_mouse_moved(self, sender, data):
        self.mouse_stats.mouse_pos = data

        # TODO: Move this logic below off of the UI thread and post an update once the specific data needs to refresh

        # TODO: Need to handle cases where the parent is also in a parent
        # TODO: Total offset is the offset of all parents for children of children etc
        self.mouse_stats.mouse_offset = dpg.get_item_pos('md_panel')
        if self.mouse_stats.is_down:
            indices = self.mouse_stats.translate_pos_to_indices(self.measure_boundaries)
            # indices = [note_index, slot_index]
            if indices is None:
                return

            # toggle the index (for now instead of changing between sets of values)
            val = self.slots[indices[0]][indices[1]]
            self.slots[indices[0]][indices[1]] = not val

            # we need to configure this item now (this works but we shouldn't constantly toggle as we move -- need to do only once per down)
            fill = [0, 255, 0, 255] if val == 1 else [255, 255, 255, 255]
            dpg.configure_item('r[{row}][{col}]'.format(row=indices[0], col=indices[1]), fill=fill)


    def panel_mouse_down(self, sender, data):
        if self.mouse_stats.trigger():
            print('panel_mouse_down: {d}'.format(d=data))
            print('info: {i}'.format(i=dpg.get_item_info('md_panel')))
            print('item pos: {p}'.format(p=dpg.get_item_pos('md_panel')))

            self.panel_mouse_moved(sender, self.mouse_stats.mouse_pos)

    def panel_mouse_up(self, sender, data):
        print('panel_mouse_up: {d}'.format(d=data))
        self.mouse_stats.clear()

    def draw(self, parent):
        cols = self.slots_per_measure * self.num_measures
        rows = self.notes_per_octave * self.num_octaves

        if not dpg.does_item_exist('md_panel'):
            dpg.add_child(parent=parent, id='md_panel', width=self.width, height=self.height, horizontal_scrollbar=True)

            with dpg.theme(id="no_padding_theme"):
                dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 0, 0, category=dpg.mvThemeCat_Core)
                dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 0, 0, category=dpg.mvThemeCat_Core)
            dpg.set_item_theme(item='md_panel', theme='no_padding_theme')
            dpg.set_item_theme(item=parent, theme='no_padding_theme')

        content_width = (cols * MeasuresDisplay.slot_width) + (MeasuresDisplay.measure_spacing * self.num_measures)
        content_height = (self.octave_height * self.num_octaves) + (MeasuresDisplay.octave_spacing * self.num_octaves)
        if dpg.does_item_exist('md_dl'):
            dpg.delete_item('md_dl', children_only=True)
        else:
            dpg.add_drawlist(parent='md_panel', id='md_dl', width=content_width + self.scrollbar_offset, height=content_height)

        # cycle over the prepared data and actually draw
        self.measure_boundaries.clear()
        cur_boundary = {}
        for i_iter, i in enumerate(self.slots):
            octave_index = int(i_iter / self.notes_per_octave)
            y = (i_iter * MeasuresDisplay.slot_height) + (octave_index * MeasuresDisplay.octave_spacing)

            # new row
            is_octave_boundary = (i_iter % self.notes_per_octave) == 0
            if is_octave_boundary:
                o_start = y
                cur_boundary = {
                    'octave': octave_index,
                    'measure': 0,
                    'x1': 0,
                    'y1': o_start,
                    'x2': 0,
                    'y2': o_start + self.octave_height
                }

            for j_iter, j in enumerate(i):
                measure_index = int(j_iter / self.slots_per_measure)
                x = (j_iter * MeasuresDisplay.slot_width) + (measure_index * MeasuresDisplay.measure_spacing)

                is_measure_boundary = (j_iter % self.slots_per_measure) == 0
                if is_measure_boundary:
                    m_start = x
                    boundary = cur_boundary.copy()
                    boundary['x1'] = m_start
                    boundary['x2'] = m_start + self.measure_width
                    boundary['measure'] = measure_index
                    self.measure_boundaries.append(boundary)

                # new slot in row
                x = (j_iter * MeasuresDisplay.slot_width) + (measure_index * MeasuresDisplay.measure_spacing)
                fill = [0, 255, 0, 255] if j == 1 else [255, 255, 255, 255]
                dpg.draw_rectangle(id='r[{row}][{col}]'.format(row=i_iter, col=j_iter), parent='md_dl', pmin=[x, y],
                                   pmax=[x + MeasuresDisplay.slot_width,
                                         y + MeasuresDisplay.slot_height],
                                   fill=fill,
                                   thickness=4,
                                   color=[0, 0, 0, 255])
                # dpg.draw_text(parent='md_dl', pos=[x + 4, y + 4], text='r[{row}][{col}]'.format(row=i_iter, col=j_iter), color=[255, 0 ,0, 255])

                note_key = MeasuresDisplay.note_mapping[(i_iter % len(MeasuresDisplay.note_mapping))]

                dpg.draw_text(parent='md_dl', size=12, pos=[x + 4, y + 4], text=note_key, color=[0, 0, 0, 255])

        for iter_m, m in enumerate(self.measure_boundaries):
            dpg.draw_rectangle(parent='md_dl',
                               fill=[150, 150, 150, 255],
                               pmin=[m['x1'], m['y2']],
                               pmax=[m['x2'], m['y2'] + MeasuresDisplay.octave_spacing])
            dpg.draw_text(parent='md_dl', pos=[m['x1'] + ((m['x2'] - m['x1']) / 2) - 25, m['y2'] + 5], size=11, text='Octave {o} Measure {m}'.format(o=m['octave'], m=m['measure']))



if __name__ == '__main__':
    dpg.add_window(id="md_test", width=1000, height=800)
    dpg.set_primary_window('md_test', True)

    dpg.setup_viewport()

    measures_display = MeasuresDisplay(dpg.get_viewport_width(), dpg.get_viewport_height() - 100, 50)
    dpg.add_dummy(parent='md_test', height=20)
    dpg.add_dummy(parent='md_test', width=20)
    dpg.add_same_line(parent='md_test')
    measures_display.draw('md_test')

    dpg.start_dearpygui()
