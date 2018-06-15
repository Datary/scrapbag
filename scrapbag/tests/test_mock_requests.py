# -*- coding: utf-8 -*-
"""
Datary MockRequestsResponse Test
"""
import unittest
from scrapbag.tests.files.mock_requests import MockRequestResponse


class MockRequestsResponseTestCase(unittest.TestCase):
    """
    MockRequestsResponse Test Case
    """

    def test(self):
        """
        Test MockRequestsResponse
        """
        test = MockRequestResponse(
            'aaaa', path='test_path', json={'test': [1, 2, 3]})
        self.assertEqual(test.text, 'aaaa')
        self.assertEqual(test.path(), 'test_path')
        self.assertEqual(test.encoding(), 'utf-8')
        self.assertEqual(test.json(), {'test': [1, 2, 3]})
