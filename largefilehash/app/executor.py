from .providers import TaskThreadProvider, PathProvider
from .calculator import Calculator
from .logger import Logger

import threading
import hashlib
from typing import IO, List


class FileHashTask():

    def __init__(self, start, end, path, path_provider=PathProvider()):
        self._start = start
        self._end = end
        self._path = path
        self._path_provider = path_provider

    def execute(self, executor, index: int):
        file_handle = self._try_open_file_for_read(executor)
        if not file_handle:
            return

        try:
            result = self._hash_section_of_file(executor, file_handle)
        except Exception as e:
            self._close_file(file_handle)
            executor.notify_failure(f'Failed to hash part of file: {str(e)}')
            return

        if result is None:
            return

        executor.checkin_hash(result, index)
        self._close_file(file_handle)

    def _hash_section_of_file(self, executor, file_handle: IO):
        iterations_made = 0
        bytes_read = 0

        next_read = self._calculate_next_read_byte_count(bytes_read)
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
            next_read = self._calculate_next_read_byte_count(bytes_read)
            if next_read <= 0:
                break  # pragma: no mutate
            bytes = file_handle.read(next_read)

        return hasher.digest()

    def _can_update_progress(self, iterations_made: int) -> bool:
        return iterations_made % Calculator.iterations_between_feedback == 0

    def _calculate_next_read_byte_count(self, read: int) -> int:
        remaining = (self._end - self._start) - read
        if remaining > Calculator.max_bytes_per_read:
            return Calculator.max_bytes_per_read
        return remaining

    def _try_open_file_for_read(self, executor) -> IO:
        try:
            return self._path_provider.open_file_for_binary_read(self._path)
        except Exception as e:
            executor.notify_failure(f'Failed to open file to read: {str(e)}')
            return None

    def _close_file(self, handle):
        try:
            handle.close()
        except Exception:
            pass


TaskList = List[FileHashTask]  # pragma: no mutate


class FailureManager():

    def __init__(self):
        self._failed = False
        self._failure_reason = ''  # pragma: no mutate
        self._fail_lock = threading.Lock()

    def has_failed(self) -> bool:
        with self._fail_lock:
            return self._failed

    def notify_failure(self, reason: str):
        with self._fail_lock:
            if self._failed:
                return
            self._failed = True
            self._failure_reason = reason

    def failure_reason(self) -> str:
        with self._fail_lock:
            return self._failure_reason


class HashManager():

    def __init__(self, num_of_hashes: int):
        self._hashes = [None for i in range(num_of_hashes)]
        self._check_in_lock = threading.Lock()
        self._checked_in_count = 0

    def get_hashes(self) -> List[str]:
        with self._check_in_lock:
            return self._hashes

    def is_complete_after_check_in(self, hash_value: str, index: int) -> bool:
        with self._check_in_lock:
            self._check_in_hash(hash_value, index)
            return self._are_all_hashes_checked_in()

    def _check_in_hash(self, hash_value: str, index: int):
        if self._are_all_hashes_checked_in():
            return
        self._checked_in_count = self._checked_in_count + 1
        self._hashes[index] = hash_value

    def _are_all_hashes_checked_in(self) -> bool:
        return self._checked_in_count == len(self._hashes)


class FileHashTaskExecutor():

    progress_message = 'Hashing file...'

    def __init__(self, logger: Logger, tasks: TaskList, thread_provider=TaskThreadProvider()):
        self._thread_provider = thread_provider
        self._continue_condition = threading.Condition()

        self._hash_manager = HashManager(len(tasks))

        self._failure_manager = FailureManager()

        self._task_threads = self._create_task_threads(tasks)

        self._logger_lock = threading.Lock()
        self._logger = logger

    def _create_task_threads(self, tasks: TaskList) -> List:
        return [self._thread_provider.provide_thread(tasks[i], self, i) for i in range(len(tasks))]

    def execute_all_tasks(self):
        for thread in self._task_threads:
            thread.start()

        self._wait_to_complete()

        if self._failure_manager.has_failed():
            raise Exception(self._failure_manager.failure_reason())

        return self._hash_manager.get_hashes()

    def _wait_to_complete(self):
        with self._continue_condition:
            self._continue_condition.wait()

        for thread in self._task_threads:
            thread.join()

    def has_failed(self) -> bool:
        return self._failure_manager.has_failed()

    def checkin_hash(self, hash_value: str, index: int):
        if self._hash_manager.is_complete_after_check_in(hash_value, index):
            with self._continue_condition:
                self._continue_condition.notifyAll()

    def notify_failure(self, reason: str):
        self._failure_manager.notify_failure(reason)
        with self._continue_condition:
            self._continue_condition.notifyAll()

    def on_progress_made(self):
        with self._logger_lock:
            self._logger.tick_progress(FileHashTaskExecutor.progress_message)
