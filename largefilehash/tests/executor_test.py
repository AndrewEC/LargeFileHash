import unittest
from unittest.mock import MagicMock, Mock, call

import threading
import time

from ..src import FileHashTaskExecutor


class FileHashTaskExecutorTest(unittest.TestCase):

    number_of_tasks = 5

    def setUp(self):
        self.mock_logger = MagicMock()
        self.mock_thread_provider = MagicMock()
        self.mock_thread_provider.provide_thread = Mock()

    def test_execute_tasks(self):
        self.mock_thread_provider.provide_thread.side_effect = provide_thread

        tasks = [MagicMock() for i in range(FileHashTaskExecutorTest.number_of_tasks)]
        executor = FileHashTaskExecutor(self.mock_logger, tasks, self.mock_thread_provider)

        results = executor.execute_all_tasks()

        self.assertEqual(FileHashTaskExecutorTest.number_of_tasks, len(results))
        for i in range(len(results)):
            self.assertEqual(f'testing-{i}', results[i])

        calls = [call(tasks[i], executor, i) for i in range(len(tasks))]
        self.mock_thread_provider.provide_thread.assert_has_calls(calls)

    def test_execute_tasks_with_error_in_first_task(self):
        self.mock_thread_provider.provide_thread.side_effect = provide_failing_thread
        tasks = [MagicMock()]
        executor = FileHashTaskExecutor(self.mock_logger, tasks, self.mock_thread_provider)

        with self.assertRaises(Exception) as context:
            executor.execute_all_tasks()

        self.assertEqual(FailingMockThread.failure_message, str(context.exception))

    def test_on_progress_made(self):
        tasks = [MagicMock()]
        executor = FileHashTaskExecutor(self.mock_logger, tasks, self.mock_thread_provider)

        executor.on_progress_made()

        self.mock_logger.tick_progress.assert_called_once_with('Hashing file...')

    def test_notify_failure(self):
        reason = 'failure reason'
        tasks = [MagicMock()]
        executor = FileHashTaskExecutor(self.mock_logger, tasks, self.mock_thread_provider)

        executor.notify_failure(reason)

        self.assertTrue(executor.has_failed())
        self.assertEqual(reason, executor._failure_manager.failure_reason())


def provide_failing_thread(task, executor, index):
    return FailingMockThread(task, executor, index)


def provide_thread(task, executor, index):
    return MockThread(task, executor, index)


class FailingMockThread(threading.Thread):

    failure_message = 'test failure message'

    def __init__(self, task, executor, index):
        super().__init__()
        self._executor = executor

    def run(self):
        time.sleep(.25)
        self._executor.notify_failure(FailingMockThread.failure_message)


class MockThread(threading.Thread):

    def __init__(self, task, executor, index):
        super().__init__()
        self.executor = executor
        self.start_called = False
        self.index = index

    def run(self):
        time.sleep(.25)
        self.start_called = True
        self.executor.checkin_hash(f'testing-{self.index}', self.index)
