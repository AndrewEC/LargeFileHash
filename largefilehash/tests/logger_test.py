import unittest
from unittest.mock import MagicMock

from ..src import Logger


class LoggerTest(unittest.TestCase):

    max_progress = 10

    def setUp(self):
        self.mock_printer = MagicMock()
        self.logger = Logger(LoggerTest.max_progress, self.mock_printer)

    def test_print_message(self):
        message = 'message to print'

        self.logger.print(message)

        self.mock_printer.print.assert_called_once_with(message)

    def test_print_percentage(self):
        arguments = [
            ('long message long message', '[==------------------] 10% - {}\r'),
            ('short message', '[====----------------] 20% - {}            \r'),
            ('medium message', '[======--------------] 30% - {}\r')
        ]

        for i in range(len(arguments)):
            with self.subTest():
                argument = arguments[i]
                self.logger.tick_progress(argument[0])

                self.mock_printer.print_same_line.assert_called_with(argument[1].format(argument[0]))
                self.mock_printer.print_same_line.reset_mock()

    def test_print_complete(self):
        message = 'message to print'

        self.logger.complete(message)

        self.mock_printer.print.assert_called_once_with(message)
        self.assertEqual(0, self.logger._last_string_length)
        self.assertEqual(self.logger._max_progress, self.logger._current_progress)
