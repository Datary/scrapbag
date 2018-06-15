# -*- coding: utf-8 -*-
"""
Datary Mock_Csv Test
"""
import unittest
from scrapbag.tests.files.mock_csv import MockSheet, MockCell


class MockSheetTestCase(unittest.TestCase):
    """
    MockSheet Test Case
    """

    def test(self):
        """
        Test MockSheet        """
        test_list = [[1, 2, 3], [4, 5, 6]]
        test_merged_cells = [(0, 1, 1, 2), (3, 4, 1, 2)]
        test = MockSheet(test_list, merged_cells=test_merged_cells)
        self.assertEqual(isinstance(test.cells, list), True)
        self.assertEqual(len(test.cells), len(test_list))
        self.assertEqual(isinstance(test.cell(0, 2), MockCell), True)
        self.assertEqual(test.cell(0, 2).value, 3)
        self.assertEqual(test.ncols, 3)
        self.assertEqual(test.nrows, 2)
        self.assertEqual(test.merged_cells, test_merged_cells)
