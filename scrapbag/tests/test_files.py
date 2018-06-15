# -*- coding: utf-8 -*-
"""
Test Scrapbag files file
"""
import time
import unittest
import mock

from scrapbag.tests.files.mock_requests import MockRequestResponse
from scrapbag.files import (
    open_filezip,
    extract_filezip,
    download_file,
    open_remote_url,
    is_remote_file_modified,
    copy_remote_file,
    remove_file
    )


class UtilsFilesTestCase(unittest.TestCase):
    """
    Scrapbag files Test CaseW
    """

    url = "http://test_url.com/test.csv"

    @mock.patch('zipfile.ZipFile')
    @mock.patch('zipfile.is_zipfile')
    def test_openzipfile(self, mock_iszip, mock_zipfile):
        """
        Test open_zipfile
        """
        mock_zipfile.return_value.configure_mock(**{
            'infolist.return_value': ['file1.txt', 'file2.csv', 'file2.txt'],
            'open.return_value': True,
        })
        mock_iszip.return_value = 'True'
        files = list(open_filezip('test.zip', '2'))

        mock_iszip.return_value = False
        files2 = list(open_filezip('test.meme', '2'))

        self.assertEqual(mock_iszip.call_count, 2)
        self.assertEqual(len(files), 2)
        self.assertEqual(len(files2), 0)

    @mock.patch('zipfile.ZipFile')
    @mock.patch('scrapbag.files.open', create=True)
    def test_extract_filezip(self, mock_open, mock_zipfile):
        """
        Test extract_filezip
        """

        files = ['file1.txt', 'file2.csv', 'file2.txt']

        mock_zipfile.configure_mock(**{
            'return_value.__enter__.return_value.namelist.return_value': files,
        })

        # extract only csv target
        result1 = extract_filezip('test.zip', 'dest_path', [r'.*\.csv'])

        # extract not existing target
        result2 = extract_filezip('test.zip', 'dest_path', [r'.*\.png'])

        # extract not existing target
        result3 = extract_filezip(
            'test.zip', 'dest_path', [r'.*\.png', r'.*\.csv'])

        # extract all without target
        result4 = extract_filezip('test.zip', 'dest_path', [])

        # extract all with target
        result5 = extract_filezip(
            'test.zip', 'dest_path', [r'.*\.csv', r'.*\.txt'])

        # force exception during extraction
        mock_zipfile__enter = mock_zipfile.return_value.__enter__
        mock_zipfile__enter.return_value.extract.side_effect = [
            True, Exception('Error extracting file'), False]
        result6 = extract_filezip(
            'test.zip', 'dest_path', [r'.*\.csv', r'.*\.txt'])

        result7 = extract_filezip('badzip.bad', 'dest_path')

        self.assertEqual(len(result1), 1)
        self.assertEqual(isinstance(result1, list), True)
        self.assertEqual(mock_open.call_count, 6)
        self.assertEqual(mock_open.return_value.close.call_count, 6)

        self.assertEqual(result2, [])
        self.assertEqual(result3, result1)

        self.assertEqual(result4, ['dest_path/%s' % (x,) for x in files])

        self.assertEqual(result5, result4)

        self.assertEqual(len(result6), 2)

        self.assertEqual(result7, [])

    @mock.patch('scrapbag.files.is_remote_file_modified')
    @mock.patch('scrapbag.files.copy_remote_file')
    @mock.patch('scrapbag.files.open_remote_url')
    def test_download_file(self, mock_open, mock_copy, mock_modified):
        """
        Test download_file
        """
        destination = "test_path/test_destination/"

        mock_open.return_value.configure_mock(**{
            'url': self.url,
            'close.return_value': True
        })

        mock_modified.return_value = True

        download_file(self.url, destination)
        self.assertTrue(mock_open.called)
        self.assertTrue(mock_modified.called)
        self.assertTrue(mock_copy.called)

        mock_copy.reset_mock()
        mock_open.reset_mock()
        mock_modified.reset_mock()

        mock_modified.return_value = False
        download_file(self.url, destination)

        self.assertFalse(mock_copy.called)
        self.assertTrue(mock_open.called)
        self.assertTrue(mock_modified.called)

        mock_open.return_value = False
        mock_modified.reset_mock()
        download_file(self.url, destination)

        self.assertFalse(mock_modified.called)

    @mock.patch('scrapbag.files.requests')
    def test_open_remote_url(self, mock_requests):
        """
        Test open_remote_url
        """

        mock_requests.get.return_value = MockRequestResponse(
            "ok", headers={'content-type': 'x-form-test'})
        result = open_remote_url(self.url)
        result2 = open_remote_url([self.url])

        self.assertIsNot(result, None)
        self.assertIsNot(result2, None)

        self.assertEqual(mock_requests.get.call_count, 2)

        mock_requests.get.return_value = MockRequestResponse(
            "ok", headers={'content-type': 'html'})
        result3 = open_remote_url([self.url])
        self.assertEqual(result3, None)

        mock_requests.side_effect = Exception('Test exception')
        result4 = open_remote_url([self.url])
        self.assertEqual(result4, None)

    @mock.patch('scrapbag.files.os.path.getmtime')
    @mock.patch('scrapbag.files.os.path.getsize')
    @mock.patch('scrapbag.files.os.path.exists')
    @mock.patch('scrapbag.files.time.gmtime')
    def test_is_remote_file_modified(self,
                                     mock_time,
                                     mock_exists,
                                     mock_getsize,
                                     mock_getmtime):
        """
        Test is_remote_file_modified
        """

        web_file_test = MockRequestResponse("ok", headers={
            'last-modified': 'Thu, 15 Sep 2016 12:03:01 GMT',
            'content-length': 123})

        test_time = time.strptime(
            web_file_test.headers['last-modified'], '%a, %d %b %Y %H:%M:%S %Z')

        mock_exists.return_value = True
        mock_getmtime.return_value = web_file_test.headers['last-modified']
        mock_getsize.return_value = web_file_test.headers['content-length']
        mock_time.return_value = test_time

        # no changed
        result = is_remote_file_modified(
            web_file_test, 'destination/test/file.csv')

        # change the last_modify param
        web_file_test.headers[
            'last-modified'] = 'Thu, 22 Sep 2016 12:03:01 GMT'
        result2 = is_remote_file_modified(
            web_file_test, 'destination/test/file.csv')

        # change the last_modify param & content_length
        web_file_test.headers['content-length'] = 456
        result3 = is_remote_file_modified(
            web_file_test, 'destination/test/file.csv')

        # change only content-length
        web_file_test.headers[
            'last-modified'] = 'Thu, 15 Sep 2016 12:03:01 GMT'
        web_file_test.headers['content-length'] = 456
        result4 = is_remote_file_modified(
            web_file_test, 'destination/test/file.csv')

        # destination doesnt exists
        mock_exists.return_value = False
        result5 = is_remote_file_modified(
            web_file_test, 'destination/test/file.csv')

        # no last_modified in headers
        web_file_test.headers['last-modified'] = None
        result6 = is_remote_file_modified(
            web_file_test, 'destination/test/file.csv')

        web_file_test.headers[
            'last-modified'] = 'Thu, 15 Sep 2016 12:03:01 GMT'
        web_file_test.headers['content-length'] = None
        result7 = is_remote_file_modified(
            web_file_test, 'destination/test/file.csv')

        mock_exists.side_effect = Exception('Test exception')
        result8 = is_remote_file_modified(
            web_file_test, 'destination/test/file.csv')

        self.assertEqual(result, False)
        self.assertEqual(result2, True)
        self.assertEqual(result3, True)
        self.assertEqual(result4, True)
        self.assertEqual(result5, True)
        self.assertEqual(result6, True)
        self.assertEqual(result7, True)
        self.assertEqual(result8, True)

    @mock.patch('scrapbag.files.open', create=True)
    @mock.patch('scrapbag.files.os.makedirs')
    @mock.patch('scrapbag.files.os.path.exists')
    def test_copy_remote_file(self, mock_exists, mock_makedirs, mock_open):
        """
        Test copy_remote_file
        """

        class WebFile:
            """
            Web file testing class
            """

            def __init__(self, value, **kwargs):
                """
                init webfile method
                """
                self.value = value
                self.stored = iter(value)

            def iter_content(self, **kwargs):
                """
                iter content method
                """
                return self.stored

            def reset(self):
                """
                reset method
                """
                self.stored = iter(self.value)

        # TODO: Refactor Webfile class.
        test_web_file = WebFile(['2', '3', None])

        mock_exists.return_value = True
        mock_makedirs.return_value = True
        mock_open.return_value = mock.MagicMock()

        copy_remote_file(test_web_file, 'test_path/path/file.csv')
        self.assertFalse(mock_makedirs.called)

        test_web_file.reset()
        mock_exists.return_value = False
        copy_remote_file(test_web_file, 'test_path/path/file.csv')
        self.assertTrue(mock_makedirs.called)

    @mock.patch('scrapbag.files.os.remove')
    @mock.patch('scrapbag.files.os.path.exists')
    def test_remove_file(self, mock_exists, mock_remove):
        """
        Test remove_file
        """
        mock_exists.return_value = True
        path = "test_path/dest/file.csv"

        remove_file(path)
        self.assertTrue(mock_remove.called)

        mock_remove.reset_mock()
        mock_exists.return_value = False
        remove_file(path)
        self.assertFalse(mock_remove.called)
