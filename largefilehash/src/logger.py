import math
from .providers import PrintProvider


class Logger():

    progress_bar_length = 20

    def __init__(self, max_progress: int, printer=PrintProvider()):
        self._printer = printer
        self._max_progress = max_progress
        self._current_progress = 0
        self._last_string_length = 0

    def print(self, to_print: str):
        self._printer.print(to_print)

    def tick_progress(self, to_print: str):
        progress_percent = self._calculate_progress_percentage()
        progress_bar = self._create_progress_bar(progress_percent)
        progress_percent = math.floor(progress_percent * 100)
        message = self._pad_message_with_spaces(f'{progress_bar} {progress_percent}% - {to_print}')
        self._printer.print_same_line(f'{message}\r')

    def complete(self, to_print: str):
        message = self._pad_message_with_spaces(to_print)
        self._printer.print(message)

    def _calculate_progress_percentage(self) -> float:
        self._current_progress = self._current_progress + 1
        return self._current_progress / self._max_progress

    def _create_progress_bar(self, progress_message: str) -> str:
        number_of_positive_ticks = int(progress_message * Logger.progress_bar_length)
        number_of_negative_ticks = Logger.progress_bar_length - number_of_positive_ticks

        positive = '=' * number_of_positive_ticks
        negative = '-' * number_of_negative_ticks

        return f'[{positive}{negative}]'

    def _pad_message_with_spaces(self, message: str) -> str:
        padded_message = message
        message_length = len(message)
        if message_length < self._last_string_length:
            padding = ' ' * (self._last_string_length - message_length)
            padded_message = f'{padded_message}{padding}'
        self._last_string_length = message_length
        return padded_message
