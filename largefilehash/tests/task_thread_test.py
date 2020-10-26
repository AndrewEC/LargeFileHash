import unittest
from unittest.mock import MagicMock
from ..src import TaskThread


class TaskThreadTest(unittest.TestCase):

    def test_execute_task(self):
        index = 100
        mock_task = MagicMock()
        mock_executor = MagicMock()

        task_thread = TaskThread(mock_task, mock_executor, index)

        task_thread.start()
        task_thread.join()

        mock_task.execute.assert_called_once_with(mock_executor, index)

    def test_execute_with_exception_in_task(self):
        exception_message = 'exception message'

        index = 100
        mock_task = MagicMock()
        mock_executor = MagicMock()
        mock_task.execute.side_effect = Exception(exception_message)

        task_thread = TaskThread(mock_task, mock_executor, index)

        task_thread.start()
        task_thread.join()

        mock_executor.notify_failure.assert_called_once_with(exception_message)
