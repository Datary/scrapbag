# -*- coding: utf-8 -*-
"""
Test Scrapbag spss file
"""
import os

import mock
import unittest

from scrapbag.spss import (
    parse_spss_header_leyend,
    parse_variable_label,
    parse_value_label,
    parse_spss_headerfile,
    parse_spss_datafile,
    join_spss_header_data,
    parse_spss,
    )


class UtilsSpssTestCase(unittest.TestCase):

    def setUp(self):
        """
        Setup 3 test case from cis with differents formats to test parser.
        """
        self.SPSS_ROOT_PATH = 'scrapbag/tests/files/spss'

        self.spss_path1 = os.path.join(self.SPSS_ROOT_PATH, 'MD3193_2017')
        self.spss_path2 = os.path.join(self.SPSS_ROOT_PATH, 'MD2967_2012')
        self.spss_path3 = os.path.join(self.SPSS_ROOT_PATH, 'MD2564_2004')

        self.header_filepath3 = os.path.join(self.spss_path1, 'ES3193')
        self.data_filepath3 = os.path.join(self.spss_path1, 'DA3193')

        self.header_filepath2 = os.path.join(self.spss_path2, 'ES2967')
        self.data_filepath2 = os.path.join(self.spss_path2, 'DA2967')

        self.header_filepath1 = os.path.join(self.spss_path3, 'ES2564')
        self.data_filepath1 = os.path.join(self.spss_path3, 'DA2564')

    @mock.patch('scrapbag.spss.add_element')
    def test_parse_spss_header_leyend(self, mock_add_element):

        mock_add_element.side_effect = Exception('Test Exception')
        self.assertEqual(parse_spss_header_leyend(''), {})

    @mock.patch('scrapbag.spss.add_element')
    def test_parse_variable_label(self, mock_add_element):
        header = {'a': 123}
        mock_add_element.side_effect = Exception('Test Exception')
        self.assertEqual(parse_variable_label(["/P1401 'Hasta ahora'\r\n/P1401 'Hasta ahora'"], header), None)
        self.assertEqual(header, {'a': 123})

    def test_parse_value_label(self):

        pass

    def test_parse_spss_header_labels(self):

        pass

    def test_parse_spss_headerfile(self):

        pass

    def test_parse_spss_header_values(self):

        pass

    def test_parse_spss_datafile(self):

        pass

    def test_join_spss_header_data(self):

        pass

    def test_parse_spss_header_data_file(self):

        header1 = parse_spss_headerfile(self.header_filepath1)
        header2 = parse_spss_headerfile(self.header_filepath2)
        header3 = parse_spss_headerfile(self.header_filepath3)

        with mock.patch('scrapbag.spss.parse_spss_header_leyend') as mock_parse_leyend:
            mock_parse_leyend.return_value = None
            bad_header4 = parse_spss_headerfile(self.header_filepath1)
            self.assertEqual(bad_header4, {})

        # previus reviewed the header file
        self.assertEqual(len(header1), 62)
        self.assertEqual(len(header2), 172)
        self.assertEqual(len(header3), 162)

        data1 = parse_spss_datafile(self.data_filepath1)
        data2 = parse_spss_datafile(self.data_filepath2)
        data3 = parse_spss_datafile(self.data_filepath3)

        # previus reviewed the data files
        self.assertEqual(len(data1), 4781)
        self.assertEqual(len(data2), 2464)
        self.assertEqual(len(data3), 1510)

        result1 = join_spss_header_data(header1, data1)
        result2 = join_spss_header_data(header2, data2)
        result3 = join_spss_header_data(header3, data3)
        result4 = parse_spss(
            header_filepath=self.header_filepath1,
            data_filepath=self.data_filepath1)

        self.assertEqual(len(result1), 4781)
        self.assertEqual(result1, result4)
        self.assertEqual(len(result2), 2464)
        self.assertEqual(len(result3), 1510)
