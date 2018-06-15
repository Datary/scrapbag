# -*- coding: utf-8 -*-
"""
Test Scrapbag geo file
"""
import unittest
from unittest.mock import MagicMock
import mock

from scrapbag.geo import (
    get_country,
    get_location,
    get_address)


class GeoTestCase(unittest.TestCase):
    """
    Scrapbag geo Test Case
    """

    def test_get_country(self):
        """
        Test get_country
        """
        spain = get_country(name='Spain')
        spain2 = get_country(alpha_2='ES')
        spain3 = get_country(alpha_3='ESP')
        czech = get_country(name='Czech', similar=True)

        bad = get_country(alpha_2='ESP')
        bad_similar = get_country(name='xxxlalaltest', similar=True)

        self.assertEqual(spain.alpha_2, 'ES')
        self.assertEqual(spain.alpha_3, 'ESP')
        self.assertEqual(spain, spain2)
        self.assertEqual(spain, spain3)
        self.assertEqual(czech.official_name, 'Czech Republic')
        self.assertEqual(bad, None)
        self.assertEqual(bad_similar, None)

    @mock.patch('scrapbag.geo.Nominatim')
    def test_get_location(self, mock_nominatim):
        """
        Test get_location
        """

        mock_nominatim.return_value.geocode.return_value = MagicMock(
            latitude=2.111, longitude=-1.222)
        coordinates = get_location('test_address')
        self.assertTrue(isinstance(coordinates, tuple))
        self.assertEqual(len(coordinates), 2)

        mock_nominatim.return_value.geocode.side_effect = Exception(
            "Error in geocode method")
        coordinates = get_location('test_address')

        self.assertEqual(coordinates, None)

    @mock.patch('scrapbag.geo.Nominatim')
    def test_get_address(self, mock_nominatim):
        """
        Test get_address
        """
        mock_nominatim.return_value.reverse.return_value = MagicMock(
            address="test address")
        address = get_address((2.111, -1.222))
        self.assertTrue(isinstance(address, str))
        self.assertEqual(address, "test address")

        # test latitude & longitude args
        address = None
        address = get_address(latitude=2.111, longitude=-1.222)
        self.assertEqual(address, "test address")

        # test location arg
        address = None
        address = get_address(location=(2.111, -1.222))
        self.assertEqual(address, "test address")

        # test only latitude
        address = None
        address = get_address(latitude=2.111)
        self.assertEqual(address, "test address")

        # test raise exception
        mock_nominatim.return_value.reverse.side_effect = Exception(
            "Error in geocode method")
        address = get_address('test_address')
        self.assertEqual(address, None)
