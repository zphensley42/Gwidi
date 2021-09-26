import concurrent.futures
import threading
import multiprocessing

# TODO: concurrent futures allows us to exec a list of tasks, but not a rolling window of them as a 'task queue' would imply

# multiprocessing.pool.ThreadPool

executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)

# class TaskScheduler(threading.Thread):
#     def __init__(self):
#         self.alive = True
#         threading.Thread.__init__(self)
#
#     def schedule(self, task):
#         global executor
#         f = executor.submit()
#         concurrent.futures.wait(f)


futures = []
def print_task_result(future):
    try:
        data = future.result()
    except Exception as exc:
        print('generated an exception: %s' % (exc))
    else:
        print('response data is {d}'.format(d=data))

def push_async_task(task):
    global executor
    f = executor.submit(task)
    f.add_done_callback(fn=print_task_result)
