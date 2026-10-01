import unittest
from count_nonnegative import count_nonnegative


class CountNonnegativeTests(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(count_nonnegative([]), 0)

    def test_mixed(self):
        self.assertEqual(count_nonnegative([-2, 0, 3]), 2)

    def test_positive(self):
        self.assertEqual(count_nonnegative([1, 2, 3]), 3)


if __name__ == '__main__':
    unittest.main()
