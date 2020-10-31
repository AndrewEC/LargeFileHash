import threading
import hashlib
from typing import List

import click

from .app.validate import validate_path, validate_thread_count
from .app.executor import FileHashTaskExecutor, FileHashTask
from .app.calculator import Calculator
from .app.logger import Logger

TaskList = List[FileHashTask]


class Launcher():

    def __init__(self, number_of_threads: int, path: str, calculator=Calculator()):
        bytes_per_thread = calculator.calculate_bytes_per_thread(path, number_of_threads)
        reads_required = calculator.calculate_total_number_of_reads_required(bytes_per_thread, number_of_threads)
        self._logger = Logger(reads_required)
        self._executor = FileHashTaskExecutor(self._logger, self._create_task_list(number_of_threads, bytes_per_thread, path))

    @property
    def executor(self) -> FileHashTaskExecutor:
        return self._executor

    def _create_task_list(self, number_of_threads: int, bytes_per_thread: int, path: str) -> TaskList:
        task_list = []
        for i in range(number_of_threads):
            start = bytes_per_thread * i
            end = start + bytes_per_thread
            task_list.append(FileHashTask(start, end, path))
        return task_list

    def hash_file(self):
        result_list = self._execute()
        if result_list is None:
            return

        pseudo_hash = self._create_pseudo_hash(result_list)
        self._logger.complete(pseudo_hash)

    def _execute(self) -> List:
        try:
            return self._executor.execute_all_tasks()
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
