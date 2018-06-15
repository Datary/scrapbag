# -*- coding: utf-8 -*-
"""
Mock response module
"""


class MockRequestResponse:
    """
    Class to mock request responses, httpretty doesn't work with proxy..
    """

    def __init__(self, body, json=None, params=None, headers=None, path="",
                 status_code=200, encoding='utf-8'):

        self.status_code = status_code
        self.headers = headers

        self.text = body
        self.params = params

        self._path = path
        self._encoding = encoding

        self._json = json

    def encoding(self):
        """
        Encoding atribute getter
        Returns: encoding introduced in MockRequestResponse class
        """
        return self._encoding

    def path(self):
        """
        Path atribute getter.
        Returns: path introduced in MockRequestResponse class
        """
        return self._path

    def json(self):
        """
        Json atribute getter
        Returns: json introduced in MockRequestResponse class
        """
        return self._json
