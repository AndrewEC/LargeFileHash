import threading
import hashlib

import click

from .src.validate import validate_path, validate_thread_count
from .src.executor import TaskExecutor, FileHashTask
from .src.calculator import Calculator
from .src.logger import Logger


def hash_file(number_of_threads, path, executor, calculator=Calculator()):
    bytes_per_thread = calculator.calculate_bytes_per_thread(path, number_of_threads)
    reads_required = calculator.calculate_total_number_of_reads_required(bytes_per_thread, number_of_threads)
    logger = Logger(reads_required)

    task_list = _create_task_list(bytes_per_thread, number_of_threads, path)
    result_list = _execute(task_list, logger, executor)
    if result_list is None:
        return

    pseudo_hash = _create_pseudo_hash(result_list)
    logger.complete(pseudo_hash)


def _create_pseudo_hash(result_list):
    hasher = hashlib.sha512()
    for result in result_list:
        hasher.update(result)
    return hasher.hexdigest()


def _execute(task_list, logger, executor):
    try:
        return executor.execute_all_tasks(logger, task_list)
    except Exception as e:
        logger.complete(str(e))
        return None


def _create_task_list(bytes_per_thread, number_of_threads, path):
    task_list = []
    for i in range(number_of_threads):
        start = bytes_per_thread * i
        end = start + bytes_per_thread
        task_list.append(FileHashTask(start, end, path))
    return task_list


@click.command()
@click.argument('path')
@click.option('--threads', default=1, help='The number of threads to use to hash the file')
def main(path, threads):
    '''
    path : str : the absolute or relative path to the file to hash
    '''
    try:
        validate_path(path)
        validate_thread_count(threads)
    except Exception as e:
        print(str(e))

    executor = TaskExecutor()
    try:
        thread = threading.Thread(target=hash_file, args=(threads, path, executor))
        thread.start()
        while thread.is_alive():
            thread.join(0.25)
    except KeyboardInterrupt:
        executor.notify_failure('User interrupted process')


if __name__ == '__main__':
    main()
