import unittest
from unittest.mock import MagicMock, Mock

from ..src import Calculator


class CalculatorTest(unittest.TestCase):

    def test_with_mocks(self):
        stub_path_provider = MagicMock()
        stub_path_provider.get_file_size_bytes = Mock(return_value=100)
        path = 'testing'

        calc = Calculator(stub_path_provider)
        bytes_per_thread = calc.calculate_bytes_per_thread(path, 10)

        self.assertEqual(10, bytes_per_thread)
        stub_path_provider.get_file_size_bytes.assert_called_once_with(path)


if __name__ == '__main__':
    unittest.main()
