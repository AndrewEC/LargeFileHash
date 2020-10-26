import unittest
from unittest.mock import MagicMock, Mock, call
import math

from ..src import FileHashTask, Calculator


class FileHashTaskTest(unittest.TestCase):

    def test_execute(self):
        path = 'testing'
        target_end = Calculator.max_bytes_per_read + (Calculator.max_bytes_per_read * (Calculator.iterations_between_feedback * 2)) + (Calculator.max_bytes_per_read / 2)

        mock_path_provider = MagicMock()
        mock_file_handle = MagicMock()
        mock_file_handle.read.side_effect = [b' ' * Calculator.max_bytes_per_read for i in range(math.ceil(target_end / Calculator.iterations_between_feedback))]
        mock_path_provider.open_file_for_binary_read = Mock(return_value=mock_file_handle)

        mock_executor = MagicMock()
        mock_executor.has_failed = Mock(return_value=False)

        task = FileHashTask(Calculator.max_bytes_per_read, target_end, path, mock_path_provider)

        task.execute(mock_executor, 1)

        self.assertTrue(mock_file_handle.close.called)
        mock_file_handle.seek.assert_called_once_with(Calculator.max_bytes_per_read, 0)
        mock_executor.notify_failure.assert_not_called()
        mock_path_provider.open_file_for_binary_read.assert_called_once_with(path)

        mock_file_handle.read.assert_has_calls([call(Calculator.max_bytes_per_read), call(Calculator.max_bytes_per_read / 2)])
        self.assertTrue(mock_executor.checkin_hash.called)
        self.assertEqual(2, mock_executor.on_progress_made.call_count)

    def test_execute_when_exception_is_raised_while_opening_file(self):
        message = 'exception message'
        mock_path_provider = MagicMock()
        mock_path_provider.open_file_for_binary_read.side_effect = Exception(message)
        mock_executor = MagicMock()

        task = FileHashTask(4096, 10240, 'testing', mock_path_provider)

        task.execute(mock_executor, 1)

        mock_executor.notify_failure.assert_called_once_with(f'Failed to open file to read: {message}')

    def test_execute_when_exception_is_raised_while_reading_file(self):
        message = 'exception message'
        mock_executor = MagicMock()
        mock_file_handle = MagicMock()
        mock_file_handle.read.side_effect = Exception(message)
        mock_path_provider = MagicMock()
        mock_path_provider.open_file_for_binary_read = Mock(return_value=mock_file_handle)

        task = FileHashTask(4096, 10240, 'testing', mock_path_provider)

        task.execute(mock_executor, 1)

        mock_executor.notify_failure.assert_called_once_with(f'Failed to hash part of file: {message}')
