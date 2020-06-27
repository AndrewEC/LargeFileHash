import unittest
import os
from ..src import default_path_provider


class PathProviderTest(unittest.TestCase):

    def test_get_file_size_in_bytes(self):
        path = './largefilehash/tests/data/mock_file.txt'
        expected = os.path.getsize(path)

        actual = default_path_provider.get_file_size_bytes(path)

        self.assertEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()
