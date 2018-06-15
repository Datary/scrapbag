# -*- coding: utf-8 -*-
"""
Test Scrapbag pdf file
"""
import unittest
import mock

from scrapbag.pdf import (
    pdf_to_text,
    pdf_row_limiter,
    pdf_row_format,
    pdf_row_parser,
    pdf_row_cleaner,
    pdf_to_dict
    )


class UtilsPDFTestCase(unittest.TestCase):
    """
    Test Scrapbag pdf test case
    """

    test_rows = [
        ['test row 1 - aa', 'test row 1 - ab', 'test row 1 - ac'],
        ['test row 2 - ba', 'test row 2 - bb', 'test row 2 - bc'],
        ['test row 3 - ca', 'test row 3 - cb', 'test row 3 - cc'],
        ['test row 4 - da', 'test row 4 - db', 'test row 4 - dc'],
        ['test row 5 - ea', 'test row 5 - eb', 'test row 5 - ec']]

    @mock.patch('scrapbag.pdf.os')
    @mock.patch('scrapbag.pdf.open')
    @mock.patch('scrapbag.pdf.pdfminer.high_level')
    @mock.patch('scrapbag.pdf.StringIO')
    def test_pdf_to_text(self,
                         mock_stringio,
                         mock_pdfminer_highlevel,
                         mock_open,
                         mock_os):

        """
        Test pdf_to_text
        """

        # no exists path
        mock_os.path.exists.return_value = False
        bad_result_noexistpath = pdf_to_text()
        self.assertEqual(bad_result_noexistpath, [])
        self.assertEqual(mock_open.call_count, 0)

        # pdfminer exception
        mock_os.path.exists.return_value = True
        mock_pdfminer_extract = mock_pdfminer_highlevel.extract_text_to_fp
        mock_pdfminer_extract.side_effect = Exception("Test exception")
        bad_result_exception = pdf_to_text()
        self.assertEqual(bad_result_exception, [])
        self.assertEqual(mock_open.call_count, 1)

        mock_open.reset_mock()
        mock_pdfminer_highlevel.extract_text_to_fp.side_effect = None
        mock_stringio().getvalue.return_value = self.test_rows
        result = pdf_to_text('testfilepath')
        self.assertEqual(result, self.test_rows)
        self.assertEqual(mock_open.call_count, 1)

    def test_pdf_row_limiter(self):
        """
        Test pdf_row_limiter
        """
        no_limiter_results = pdf_row_limiter(self.test_rows)
        self.assertEqual(no_limiter_results, self.test_rows)

        x_limiter_results = pdf_row_limiter(self.test_rows, [2])
        self.assertEqual(x_limiter_results, self.test_rows[2:])

        xy_limiter_results = pdf_row_limiter(self.test_rows, [2, 5])
        self.assertEqual(xy_limiter_results, self.test_rows[2:5])

    def test_pdf_row_format(self):
        """
        Test pdf_row_format
        """
        result = pdf_row_format(self.test_rows[0])
        self.assertEqual(result, self.test_rows[0])

    def test_pdf_row_parser(self):
        """
        Test pdf_row_parser
        """
        result = pdf_row_parser(self.test_rows)
        self.assertEqual(result, self.test_rows)

    def test_pdf_row_cleaner(self):
        """
        Test pdf_row_cleaner
        """
        result = pdf_row_cleaner(['test', '', [], 'test2'])
        self.assertEqual(result, ['test', 'test2'])

    @mock.patch('scrapbag.pdf.pdf_to_text')
    @mock.patch('scrapbag.pdf.pdf_row_format')
    @mock.patch('scrapbag.pdf.pdf_row_limiter')
    @mock.patch('scrapbag.pdf.pdf_row_parser')
    @mock.patch('scrapbag.pdf.pdf_row_cleaner')
    def test_pdf_to_dict(self, mock_pdf_row_cleaner, mock_pdf_row_parser,
                         mock_pdf_row_limiter, mock_pdf_row_format,
                         mock_pdf_to_text):
        """
        Test pdf_to_dict
        """
        pdf_to_dict('testpdffilepath')
        pdf_to_dict('testpdffilepath', rows=self.test_rows)

        # only runs when no rows passed
        self.assertEqual(mock_pdf_to_text.call_count, 1)
        self.assertEqual(mock_pdf_row_format.call_count, 1)

        self.assertEqual(mock_pdf_row_limiter.call_count, 2)
        self.assertEqual(mock_pdf_row_parser.call_count, 2)
        self.assertEqual(mock_pdf_row_cleaner.call_count, 2)
