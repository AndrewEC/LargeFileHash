from .executor import TaskExecutor, FileHashTask
from .calculator import Calculator
from .logger import Logger

import hashlib


def hash_file(number_of_threads, path, calculator=Calculator()):
    bytes_per_thread = calculator.calculate_bytes_per_thread(path, number_of_threads)
    reads_required = calculator.calculate_total_number_of_reads_required(bytes_per_thread, number_of_threads)
    logger = Logger(reads_required)

    task_list = _create_task_list(bytes_per_thread, number_of_threads, path)
    result_list = _execute(task_list, logger)
    if result_list is None:
        return

    pseudo_hash = _create_pseudo_hash(result_list)
    logger.complete(pseudo_hash)


def _create_pseudo_hash(result_list):
    hasher = hashlib.sha512()
    for result in result_list:
        hasher.update(result)
    return hasher.hexdigest()


def _execute(task_list, logger):
    try:
        return TaskExecutor(logger).execute_all_tasks(task_list)
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
