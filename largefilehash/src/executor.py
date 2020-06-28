from .providers import TaskThreadProvider, PathProvider
from .calculator import Calculator
import threading
import hashlib


class FileHashTask():

    def __init__(self, start, end, path, path_provider=PathProvider()):
        self._start = start
        self._end = end
        self._path = path
        self._path_provider = path_provider

    def execute(self, executor, index):
        file_handle = self._prepare(executor)
        if not file_handle:
            return

        result = None
        try:
            result = self._do_execute(executor, file_handle)
        except Exception as e:
            self._cleanup(file_handle)
            executor.notify_failure(f'Failed to hash part of file: {str(e)}')
            return

        if result is None:
            return

        executor.checkin_hash(result, index)
        self._cleanup(file_handle)

    def _do_execute(self, executor, file_handle):
        iterations_made = 0
        bytes_read = 0

        next_read = self._calculate_next(bytes_read)
        hasher = hashlib.sha512()
        file_handle.seek(self._start, 0)
        bytes = file_handle.read(next_read)

        while bytes != b'':
            hasher.update(bytes)
            iterations_made = iterations_made + 1
            if self._can_update_progress(iterations_made):
                if executor.has_failed():
                    return None
                executor.on_progress_made()

            bytes_read = bytes_read + len(bytes)
            next_read = self._calculate_next(bytes_read)
            if next_read <= 0:
                break
            bytes = file_handle.read(next_read)

        return hasher.digest()

    def _can_update_progress(self, iterations_made):
        return iterations_made % Calculator.iterations_between_feedback == 0

    def _calculate_next(self, read):
        remaining = (self._end - self._start) - read
        if remaining > Calculator.max_bytes_per_read:
            return Calculator.max_bytes_per_read
        return remaining

    def _prepare(self, executor):
        try:
            return self._path_provider.open_file_for_binary_read(self._path)
        except Exception as e:
            executor.notify_failure(f'Failed to open file to read: {str(e)}')
            return None

    def _cleanup(self, handle):
        try:
            handle.close()
        except Exception:
            pass


class TaskExecutor():

    progress_message = 'Hashing file...'

    def __init__(self, thread_provider=TaskThreadProvider()):
        self._thread_provider = thread_provider
        self._continue_condition = threading.Condition()

        self._is_complete = False
        self._completed = 0
        self._checking_lock = threading.Lock()

        self._cancelled = False
        self._cancel_reason = ''
        self._has_failed_lock = threading.Lock()

        self._task_threads = None
        self._hashes = None

        self._logger_lock = threading.Lock()
        self._logger = None

    def execute_all_tasks(self, logger, tasks):
        self._logger = logger
        task_count = len(tasks)
        self._task_threads = [self._thread_provider.provide_thread(tasks[i], self, i) for i in range(task_count)]
        self._hashes = [None for i in range(task_count)]
        for thread in self._task_threads:
            thread.start()

        self._wait_to_complete()

        if self._cancelled:
            raise Exception(self._cancel_reason)

        return self._hashes

    def _wait_to_complete(self):
        with self._continue_condition:
            self._continue_condition.wait()

        for thread in self._task_threads:
            thread.join()

    def has_failed(self):
        with self._has_failed_lock:
            return self._cancelled

    def checkin_hash(self, hash, index):
        with self._checking_lock:
            self._hashes[index] = hash
            self._completed = self._completed + 1
            if self._completed == len(self._task_threads):
                self._is_complete = True
                with self._continue_condition:
                    self._continue_condition.notifyAll()

    def notify_failure(self, reason):
        with self._has_failed_lock:
            if self._cancelled:
                return
            self._cancelled = True
            self._cancel_reason = reason
            with self._continue_condition:
                self._continue_condition.notifyAll()

    def on_progress_made(self):
        with self._logger_lock:
            self._logger.tick_progress(TaskExecutor.progress_message)
