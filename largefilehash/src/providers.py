import os
import threading


class PathProvider():

    read_binary_mode = 'rb'

    def is_file(self, path):
        return os.path.isfile(path)

    def get_file_size_bytes(self, path):
        return os.path.getsize(path)

    def open_file_for_binary_read(self, path):
        return open(path, PathProvider.read_binary_mode)


class PrintProvider():

    def print(self, to_print):
        print(to_print)

    def print_same_line(self, to_print):
        print(to_print, end='')


class TaskThread(threading.Thread):

    def __init__(self, task, executor, index):
        super().__init__()
        self._task = task
        self._executor = executor
        self._index = index

    def run(self):
        try:
            self._task.execute(self._executor, self._index)
        except Exception as e:
            self._executor.notify_failure(str(e))


class TaskThreadProvider():

    def provide_thread(self, task, executor, index):
        return TaskThread(task, executor, index)
