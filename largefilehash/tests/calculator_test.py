import unittest
from unittest.mock import MagicMock, Mock

from ..src import Calculator


class CalculatorTest(unittest.TestCase):

    def test_calculate_bytes_per_thread(self):
        stub_path_provider = MagicMock()
        stub_path_provider.get_file_size_bytes = Mock(return_value=100)
        path = 'testing'

        calc = Calculator(stub_path_provider)
        bytes_per_thread = calc.calculate_bytes_per_thread(path, 10)

        self.assertEqual(10, bytes_per_thread)
        stub_path_provider.get_file_size_bytes.assert_called_once_with(path)

    def test_calculate_number_of_reads(self):
        arguments = [
            (4096 * 1000, 10, 100),
            (4096 * 1000, 3, 30)
        ]

        calculator = Calculator()

        for argument in arguments:
            with self.subTest():
                self.assertEqual(argument[2], calculator.calculate_total_number_of_reads_required(argument[0], argument[1]))


if __name__ == '__main__':
    unittest.main()
