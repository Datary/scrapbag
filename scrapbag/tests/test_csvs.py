# -*- coding: utf-8 -*-
"""
Test Scrapbag csv file
"""
import os
import unittest
import mock


from scrapbag.tests.files.mock_csv import MockSheet, MockCell
from scrapbag.csvs import (
    get_csv_col_headers,
    row_headers_count,
    get_row_headers,
    csv_tolist,
    excel_todictlist,
    search_mergedcell_value,
    row_csv_limiter,
    row_iter_limiter,
    csv_format,
    csv_to_dict,
    excel_to_dict
    )


UTILS_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class UtilsCSVTestCase(unittest.TestCase):
    """
    Scrapbag csv Test Case
    """

    # TODO: PUT THIS IN A TEST AUX FILE..
    test_rows = [
        ['name ', 'Explotaciones. Número', 'Explotaciones. %',
         'Superficie total. Ha.', 'Superficie total.%', 'SAU. Ha.',
         'SAU. %', ''],
        ['Explotaciones con tierras', '51591.0', '100.0', '3044707.0', '100.0',
         '2345696.0', '100.0', ''],
        ['Explotaciones sin SAU', '294.0', '0.57', '2345.0', '0.08', '0.0',
         '0.0', ''],
        ['Explotaciones con SAU', '51297.0', '99.43', '3042361.0', '99.92',
         '2345696.0', '100.0', '']
    ]

    def test_get_csv_col_headers(self):
        """
        Test get_csv_col_headers
        """

        result = get_csv_col_headers(self.test_rows)
        result2 = get_csv_col_headers(self.test_rows, 1)
        result3 = get_csv_col_headers([])

        self.assertEqual(len(result[0]), 8)
        self.assertEqual(len(result2[0]), 7)
        self.assertEqual(result3, [])

    def test_count_row_headers(self):
        """
        Test count_row_headers
        """

        count1 = row_headers_count(self.test_rows)

        self.test_rows[0][0] = ''
        self.test_rows[0][1] = ''

        count2 = row_headers_count(self.test_rows)
        count3 = row_headers_count([])
        count4 = row_headers_count([[]])

        self.assertEqual(count1, 0)
        self.assertEqual(count2, 2)
        self.assertEqual(count3, 0)
        self.assertEqual(count4, 0)

    def test_get_row_headers(self):
        """
        Test get_row_headers
        """

        test_rows = [
            ['', '', 'c1', 'c2', 'c3'],
            ['r1', 'r1a', 'a1', 'a2'],
            ['', 'r1b', 'b1', 'b2'],
            ['r1', 'r2b', 'b3', 'b4'],
            ['', 'r3b', 'b5', 'b6'],
            ['r2', 'r2c', 'c1', 'c2'],
            ['r3', 'r3d', 'd1', 'd2'],
            ['', '', 'd3', 'd4'],
        ]

        expected_rheaders = ['r1 r1a', 'r1 r1b', 'r2 r2c', 'r3 r3d']

        result = get_row_headers(test_rows, 2, 1)
        self.assertEqual(len(result), 7)
        self.assertEqual(
            all([x in result for x in expected_rheaders]), True)

    def test_retrieve_csv_data(self):
        """
        Test retrieve_csv_data
        """
        # TODO: Make test
        pass

    @mock.patch('scrapbag.csvs.open', create=True)
    @mock.patch('scrapbag.files.zipfile.ZipFile')
    @mock.patch('scrapbag.csvs.io.TextIOWrapper')
    @mock.patch('scrapbag.csvs.itertools')
    def test_csv_tolist(self,
                        mock_itertools,
                        mock_io,
                        mock_zipfile,
                        mock_open):

        """
        Test csv_tolist
        """

        mock_open.return_value = True
        mock_itertools.return_value.chain.return_value = [1, 2, 3]
        mock_io.return_value = True
        mock_zipfile.return_value.configure_mock(**{
            'namelist.return_value': ['file1.csv', 'file2.csv'],
            'open.return_value': True,
        })

        result = csv_tolist("scrapman/tests/file.zip")
        self.assertTrue(isinstance(result, list))

        mock_zipfile.return_value.configure_mock(**{
            'namelist.return_value': [],
            'open.return_value': True,
        })

        result2 = csv_tolist("scrapman/tests/file.zip")
        self.assertEqual(result2, [])

    def test_excel_todictlist(self):
        """
        Test excel_todictlist
        """
        path = os.path.join(UTILS_PATH, 'tests/files/xlsx')
        xlsx_testfile = os.path.join(path, 'xlsx_test1.xlsx')
        xlsx_testfile2_with_merges = os.path.join(path, 'xlsx_test2.xlsx')

        result = excel_todictlist(xlsx_testfile)
        result2 = excel_todictlist(xlsx_testfile2_with_merges)

        self.assertTrue(isinstance(result, dict))
        self.assertEqual(len(result.keys()), 2)

        self.assertIn('test_Sheet1', result)
        self.assertTrue(isinstance(result['test_Sheet1'], list))
        self.assertIn('test_Sheet2', result)

        self.assertTrue(isinstance(result2, dict))
        self.assertEqual(len(result.keys()), 2)
        self.assertEqual(len(result['test_Sheet2'][-1]), 4)

        self.assertIn(['', 'x', 'y', 'z', 'z'], result2['test_Sheet2'])
        self.assertEqual(len(result2['test_Sheet2'][-1]), 5)

    def test_search_mergedcell_value(self):
        """
        Test search_mergedcell_value
        """
        test = [[1, 2, 3], [4, "", ""], [7, "", ""]]
        mock_cell = MockSheet(test)

        # find 4
        self.assertEqual(isinstance(search_mergedcell_value(
            mock_cell, (1, 2, 0, 2)), MockCell), True)

        # not found anything
        self.assertEqual(isinstance(search_mergedcell_value(
            mock_cell, (1, 2, 1, 2)), MockCell), False)

        self.assertEqual(search_mergedcell_value(
            mock_cell, (0, 0, 0, 2)), False)
        self.assertEqual(search_mergedcell_value(
            mock_cell, (1, 2, 0, 0)), False)

    def test_populate_headers(self):
        """
        Test populate_headers
        """
        # TODO: Make test
        pass

    def test_row_csv_limiter(self):
        """
        Test row_csv_limiter
        """

        result = row_csv_limiter(self.test_rows)
        result2 = row_csv_limiter(self.test_rows, [])
        result3 = row_csv_limiter(self.test_rows, [2])
        result4 = row_csv_limiter(self.test_rows, [0, 2])

        self.assertEqual(result, self.test_rows)
        self.assertEqual(result2, self.test_rows)
        self.assertEqual(result3, self.test_rows[-2:])
        self.assertEqual(result4, self.test_rows[:2])

    def test_row_iter_limiter(self):
        """
        Test row_iter_limiter
        """
        self.assertEqual(row_iter_limiter([], 0, 1, 0), None)
        self.assertEqual(row_iter_limiter(
            [[1], [1, 3, 4], [4, 5, 6]], 0, 1, 0), 1)

    def test_csv_format(self):
        """
        Test csv_format
        """
        test_data = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]

        result = csv_format(
            test_data, ['c1', 'c2', 'c3'], ['r1', 'r2', 'r3'], result_format=1)
        result_strange = csv_format(test_data, result_format=1)
        result_dict = csv_format(
            test_data, ['c1', 'c2', 'c3'], ['r1', '', 'r3'], result_format=2)
        result_bad_resultformat = csv_format(
            test_data, ['c1', 'c2', 'c3'], ['r1', '', 'r3'], result_format=99)

        self.assertEqual(result_strange, [[[]] + test_data])
        self.assertEqual(
            result, [[['', 'c1', 'c2', 'c3'],
                      ['r1', 1, 2, 3],
                      ['r2', 4, 5, 6],
                      ['r3', 7, 8, 9]]])
        self.assertEqual(isinstance(result_dict, dict), True)
        self.assertEqual(len(result_dict.keys()), 2)
        self.assertEqual(result_bad_resultformat, None)

    @mock.patch('scrapbag.csvs.csv_tolist')
    def test_csv_to_dict(self, mock_csv_tolist):
        """
        Test csv_to_dict
        """
        path = os.path.join(UTILS_PATH, 'tests/files/csv')

        mock_csv_tolist.return_value = []
        with self.assertRaises(ValueError):
            csv_to_dict(os.path.join(path, 'csv_test.csv'), result_format=2)

        mock_csv_tolist.side_effect = csv_tolist
        result = csv_to_dict(os.path.join(
            path, 'csv_test.csv'), result_format=2)[0]
        result_array = csv_to_dict(os.path.join(
            path, 'csv_test.csv'), result_format=0)[0]
        result_array_clean = csv_to_dict(os.path.join(
            path, 'csv_test.csv'), result_format=1)[0]

        # perfect square csv test as dict result format
        self.assertTrue(isinstance(result, list))
        self.assertTrue(isinstance(result[0], dict))
        self.assertEqual(len(result), 12)
        self.assertEqual(len(result[0].keys()), 7)

        # perfect square csv test as array result format
        self.assertTrue(isinstance(result_array, list))
        self.assertTrue(isinstance(result_array[0], list))
        # row header present in first pos of the list
        self.assertEqual(len(result_array), 13)
        self.assertEqual(len(result_array[0]), 7)  # last space not cleaned

        # perfect square csv test as clean array result format
        self.assertTrue(isinstance(result_array_clean, list))
        self.assertTrue(isinstance(result_array_clean[0], list))
        # row header present in first pos of the list
        self.assertEqual(len(result_array_clean), 13)
        # last space not cleaned
        self.assertEqual(len(result_array_clean[0]), 7)

        # perfect square bigger csv test
        result2 = csv_to_dict(os.path.join(
            path, 'csv_test2.csv'), result_format=2)[0]
        self.assertTrue(isinstance(result2, list))
        self.assertTrue(isinstance(result2[0], dict))
        self.assertEqual(len(result2), 396)
        self.assertEqual(len(result[0].keys()), 7)

        # one row header, one column header, changing encoding and dirty rows
        # to limit
        result3 = csv_to_dict(
            os.path.join(path, 'csv_test3.csv'),
            result_format=2,
            encoding='ISO-8859-1',
            limits=[5, -5])

        self.assertTrue(isinstance(result3, dict))
        self.assertTrue(isinstance(result3[list(result3)[0]], dict))
        self.assertEqual(len(result3.keys()), 7)

        # 2 row header, 2 column header
        result4 = csv_to_dict(os.path.join(
            path, 'csv_test4.csv'), result_format=2)
        self.assertTrue(isinstance(result4, dict))
        self.assertTrue(isinstance(result4[list(result4)[0]], dict))
        self.assertEqual(len(result4.keys()), 6)

        # strange row headers
        result6 = csv_to_dict(os.path.join(
            path, 'csv_test5.csv'), result_format=2)
        self.assertTrue(isinstance(result6, dict))
        self.assertTrue(isinstance(result6[list(result6)[0]], dict))
        self.assertEqual(len(result6.keys()), 9)

        # one row only
        result7 = csv_to_dict('', rows=[['a', 'b', 'c']], result_format=2)
        self.assertEqual(result7, [[]])

    @mock.patch('scrapbag.csvs.csv_to_dict')
    @mock.patch('scrapbag.csvs.excel_todictlist')
    def test_excel_to_dict(self, mock_excel_todictlist, mock_csv_to_dict):
        """
        Test excel_to_dict
        """
        path = os.path.join(UTILS_PATH, 'tests/files/xlsx')

        mock_excel_todictlist.side_effect = excel_todictlist
        mock_csv_to_dict.side_effect = csv_to_dict

        # xlsx file
        result5_encapsulate = excel_to_dict(
            os.path.join(path, 'xlsx_test1.xlsx'),
            encapsulate_filepath=True, result_format=2)
        result5 = excel_to_dict(
            os.path.join(path, 'xlsx_test1.xlsx'),
            encapsulate_filepath=False, result_format=2)

        path_encapsulated = os.path.join(path, 'xlsx_test1.xlsx')
        self.assertIn(path_encapsulated, result5_encapsulate)
        self.assertEqual(
            len(result5_encapsulate.get(path_encapsulated, {}).keys()), 2)

        self.assertNotIn(path_encapsulated, result5)
        self.assertEqual(len(result5.keys()), 2)

        # xlsx file merged cells
        result7 = excel_to_dict(
            os.path.join(path, 'xlsx_test2.xlsx'),
            encapsulate_filepath=True, result_format=2)
        path_encapsulated = os.path.join(path, 'xlsx_test2.xlsx')
        self.assertIn(path_encapsulated, result7)

        # xlsx file merged cells
        result8 = excel_to_dict(
            os.path.join(path, 'xlsx_test2b.xls'),
            encapsulate_filepath=True, result_format=2)

        path_encapsulated = os.path.join(path, 'xlsx_test2b.xls')
        self.assertIn(path_encapsulated, result8)

        self.assertEqual(len(result8.get(path_encapsulated, {}).keys()), 4)
        self.assertEqual(result8.get(path_encapsulated, {}).get(
            'test_Sheet3', {}).get('a', {}).get('a-aa', {}), 'vaaa')
        self.assertEqual(result8.get(path_encapsulated, {}).get(
            'test_Sheet3', {}).get('b', {}).get('b-bb', {}), 'vbbb')
        self.assertEqual(result8.get(path_encapsulated, {}).get(
            'test_Sheet3', {}).get('c', {}).get('c-cb', {}), 'vcbc')

        # TODO: IN FUTURE FIX THIS CASE..
        self.assertEqual(result8.get(path_encapsulated, {}).get(
            'test_Sheet4', {}).get('c', {}).get('c-cb', {}), 'cb')

        # Excel Exceptions
        mock_csv_to_dict.side_effect = [
            csv_to_dict, Exception('Fail test exception'), csv_to_dict]
        result8_sheet_exception = excel_to_dict(
            os.path.join(path, 'xlsx_test2b.xls'),
            encapsulate_filepath=True, result_format=2)

        self.assertEqual(result8_sheet_exception.get(
            path_encapsulated, {}).get('test_Sheet2', 'not_found_key'), [])

        self.assertEqual(
            result8_sheet_exception.get(
                path_encapsulated, {}).get('test_Sheet1', 'not_found_key'),
            csv_to_dict)

        self.assertEqual(
            result8_sheet_exception.get(
                path_encapsulated, {}).get('test_Sheet3', 'not_found_key'),
            csv_to_dict)

        mock_excel_todictlist.side_effect = Exception('Err')
        result8_exception = excel_to_dict(
            os.path.join(path, 'xlsx_test2b.xls'),
            encapsulate_filepath=True, result_format=2)
        self.assertEqual(result8_exception, {})
