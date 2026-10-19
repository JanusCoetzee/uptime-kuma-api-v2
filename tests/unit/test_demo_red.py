import os, sys
import unittest


class TestDemoRed(unittest.TestCase):
    def test_fails(self):
        self.assertEqual(1, 2)
