# -*- coding: utf-8 -*-
"""
Scrapbag geo file.
"""
import structlog
from pycountry import countries
from geopy.geocoders import Nominatim
from .google import *


logger = structlog.getLogger(__name__)


def get_country(similar=False, **kwargs):
    """
    Get a country for pycountry
    """
    result_country = None
    try:
        if similar:
            for country in countries:
                if kwargs.get('name', '') in country.name:
                    result_country = country
                    break
        else:
            result_country = countries.get(**kwargs)
    except Exception as ex:
        msg = ('Country not found in pycountry with params introduced'
               ' - {}'.format(ex))
        logger.error(msg, params=kwargs)

    return result_country


def get_location(address=""):
    """
    Retrieve location coordinates from an address introduced.
    """
    coordinates = None
    try:
        geolocator = Nominatim()
        location = geolocator.geocode(address)
        coordinates = (location.latitude, location.longitude)
    except Exception as ex:
        logger.error('Fail get location - {}'.format(ex))
    return coordinates


def get_address(coords=None, **kwargs):
    """
    Retrieve addres from a location in coords format introduced.
    """
    address = None
    try:
        if (not coords) and \
            ('latitude' in kwargs and 'longitude' in kwargs) or \
                ('location' in kwargs):

            coords = kwargs.get(
                'location', (kwargs.get('latitude'), kwargs.get('longitude')))

        # transform coords
        if isinstance(coords, (list, tuple)) and len(coords) == 2:
            coords = "{}, {}".join(map(str, coords))

        geolocator = Nominatim()
        location = geolocator.reverse(coords)
        address = location.address
    except Exception as ex:
        logger.error('Fail get reverse address - {}'.format(ex))
    return address
