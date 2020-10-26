import unittest
import os
from ..src import PathProvider


class PathProviderTest(unittest.TestCase):

    def test_get_file_size_in_bytes(self):
        path = './largefilehash/tests/data/mock_file.txt'
        expected = os.path.getsize(path)

        actual = PathProvider().get_file_size_bytes(path)

        self.assertEqual(expected, actual)
