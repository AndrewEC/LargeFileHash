import threading
import hashlib
from typing import List

import click

from .src.validate import validate_path, validate_thread_count
from .src.executor import TaskExecutor, FileHashTask
from .src.calculator import Calculator
from .src.logger import Logger

TaskList = List[FileHashTask]


class Launcher():

    def __init__(self, number_of_threads: int, path: str, calculator=Calculator()):
        self._number_of_threads = number_of_threads
        self._path = path
        self._calculator = calculator
        self._bytes_per_thread = calculator.calculate_bytes_per_thread(path, number_of_threads)
        self._reads_required = calculator.calculate_total_number_of_reads_required(self._bytes_per_thread, self._number_of_threads)
        self._logger = Logger(self._reads_required)
        self._executor = TaskExecutor(self._logger)
        self._task_list = self._create_task_list()

    @property
    def executor(self) -> TaskExecutor:
        return self._executor

    def _create_task_list(self) -> TaskList:
        task_list = []
        for i in range(self._number_of_threads):
            start = self._bytes_per_thread * i
            end = start + self._bytes_per_thread
            task_list.append(FileHashTask(start, end, self._path))
        return task_list

    def hash_file(self):
        result_list = self._execute()
        if result_list is None:
            return

        pseudo_hash = self._create_pseudo_hash(result_list)
        self._logger.complete(pseudo_hash)

    def _execute(self) -> List:
        try:
            return self._executor.execute_all_tasks(self._task_list)
        except Exception as e:
            self._logger.complete(str(e))
            return None

    def _create_pseudo_hash(self, result_list: List[str]):
        hasher = hashlib.sha512()
        for result in result_list:
            hasher.update(result)
        return hasher.hexdigest()


def execute(launcher: Launcher):
    launcher.hash_file()


@click.command()
@click.argument('path')
@click.option('--threads', default=1, help='The number of threads to use to hash the file')
def main(path: str, threads: int):
    '''
    path: str : the absolute or relative path to the file to hash
    '''
    try:
        validate_path(path)
        validate_thread_count(threads)
    except Exception as e:
        print(str(e))

    launcher = Launcher(threads, path)
    executor = launcher.executor
    try:
        thread = threading.Thread(target=execute, args=(launcher,))
        thread.start()
        while thread.is_alive():  # keeps the main thread from exiting to catch user interrupts
            thread.join(0.25)
    except KeyboardInterrupt:
        executor.notify_failure('User interrupted process')


if __name__ == '__main__':
    main()
