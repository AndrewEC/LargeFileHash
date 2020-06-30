import math
from .providers import PathProvider


class Calculator():

    max_bytes_per_read = 4096
    iterations_between_feedback = 50

    def __init__(self, path_provider=PathProvider()):
        self._path_provider = path_provider

    def calculate_bytes_per_thread(self, path_to_file: str, number_of_threads: int) -> int:
        file_size_bytes = self._path_provider.get_file_size_bytes(path_to_file)
        return math.ceil(file_size_bytes / number_of_threads)

    def calculate_total_number_of_reads_required(self, bytes_per_thread: int, number_of_threads: int) -> int:
        return math.ceil((math.ceil(bytes_per_thread / Calculator.max_bytes_per_read) * number_of_threads) / Calculator.iterations_between_feedback)
