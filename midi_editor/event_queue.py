import threading, queue

# TODO: Make a message class instead of this
# Known messages:
# {'what': 1, 'desc': 'update_scrub_playout', 'params': {}}
# {'what': 2, 'desc': 'update_playout_x_scroll', 'params': {'play_time': 0}}

class Handler:
    def handles(self, m_what):
        return False

    def handle(self, msg):
        return

class UiEventQueue(threading.Thread):
    def __init__(self):
        self.msg_queue = queue.Queue()
        self.alive = True
        threading.Thread.__init__(self)

        self.handlers = []

    def push_msg(self, m):
        self.msg_queue.put(m)

    def subscribe(self, handler):
        if handler not in self.handlers:
            self.handlers.append(handler)

    def unsubscribe(self, handler):
        if handler in self.handlers:
            self.handlers.remove(handler)

    def run(self):
        while self.alive:
            msg = self.msg_queue.get()
            # to allow us to kill (push a None msg when we kill)
            print('new ui msg: {m}'.format(m=msg))
            if msg is None:
                self.msg_queue.task_done()
                continue

            # act on the msg via handler
            for h in self.handlers:
                if h.handles(msg['what']):
                    h.handle(msg)
            self.msg_queue.task_done()


g_event_queue = UiEventQueue()
g_event_queue.start()
