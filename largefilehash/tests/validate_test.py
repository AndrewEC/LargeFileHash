import unittest
from unittest.mock import MagicMock
from ..src import validate_path, validate_thread_count


class ValidateTest(unittest.TestCase):

    def test_validate_is_file_with_valid_path_doesnt_raise_exception(self):
        path = 'file path '
        mock_path_provider = MagicMock()
        mock_path_provider.is_file.return_value = True

        validate_path(path, mock_path_provider)

        mock_path_provider.is_file.assert_called_once_with(path)

    def test_validate_is_file_with_invalid_path_raises_exception(self):
        path = 'file path'
        mock_path_provider = MagicMock()
        mock_path_provider.is_file.return_value = False

        with self.assertRaises(Exception):
            validate_path(path, mock_path_provider)

    def test_validate_threads_count(self):
        invalid_arguments = [-1, 0, 13]
        for argument in invalid_arguments:
            with self.subTest():
                with self.assertRaises(Exception):
                    validate_thread_count(argument)

    def test_validate_thread_count_with_valid_thread_count(self):
        valid_arguments = [1, 11, 12]
        for argument in valid_arguments:
            with self.subTest():
                validate_thread_count(argument)


if __name__ == '__main__':
    unittest.main()
