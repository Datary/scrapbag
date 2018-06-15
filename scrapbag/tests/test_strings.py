# -*- coding: utf-8 -*-
"""
Test Scrapbag strings file
"""
import unittest
import collections

from scrapbag.collections import format_dict
from scrapbag.strings import (
    clean_text,
    clean_markdown,
    get_only_words,
    select_regexp_char,
    exclude_chars,
    normalizer,
    normalize_dict
    )


class UtilsStringsTestCase(unittest.TestCase):
    """
    Test Scrapbag test case
    """

    def test_clean_text(self):
        """
        Test clean_text
        """
        self.assertEqual(clean_text('    The   Cat   '), 'The Cat')
        self.assertEqual(clean_text(''), None)

    def test_clean_markdown(self):
        """
        Test clean_markdown
        """
        markdown_text = '####**  The   Cat  ** '
        self.assertEqual(clean_text(markdown_text), 'The Cat')
        self.assertEqual(clean_markdown([markdown_text]), [markdown_text])

    def test_get_only_words(self):
        """
        Test get_only_words
        """
        self.assertEqual(
            get_only_words('####**  The   Cat  ** '), ['The', 'Cat'])

    def test_select_regexp_char(self):
        """
        Test select_regexp_char
        """
        result = select_regexp_char('*')
        result2 = select_regexp_char('2')
        result3 = select_regexp_char([])
        result4 = select_regexp_char('a')

        self.assertEqual(result, r'\*')
        self.assertEqual(result2, '2')
        self.assertEqual(result3, '')
        self.assertEqual(result4, 'a')

    def test_exclude_chars(self):
        """
        Test exclude_chars
        """
        text = '-h**a*2!!loa12_'

        result1 = exclude_chars(text)
        result2 = exclude_chars(text, ['-', '*', '!', 'o', '1', '2', '_'])

        self.assertEqual(result1, text)
        self.assertEqual(result2, 'hala')

    def test_normalizer(self):
        """
        Test normalizer
        """
        text = 'Im @ te_[st;*ed] / `..+.  - "'
        exclusions = [' ', ',', '.', ';',
                      '@', "\\", "'", '"', "`", "[", "]", '\n']
        test_text = normalizer(text, exclusion=[])
        exclude_default = normalizer(text)

        self.assertIn('+', exclude_default)
        self.assertIn('/', exclude_default)
        self.assertIn('_', exclude_default)

        self.assertFalse(any(exc in test_text for exc in exclusions))
        self.assertNotEqual('-', test_text[-1])
        self.assertNotEqual('-', test_text[0])
        self.assertFalse(any([x.isupper() for x in test_text]))
        self.assertTrue(any([x.isupper() for x in normalizer(text, lower=False)]))

        first_step_text = normalizer(
            text, exclusion=['@'], lower=False, separate_char='')

        test_final_text_clean = normalizer(
            first_step_text, lower=False, exclusion=[], separate_char=' ')

        self.assertEqual(test_final_text_clean, 'Im tested')

    def test_normalizer_dict(self):
        """
        Test normalizer_dict
        """
        test_dict = collections.OrderedDict(
            {'a!a': 1, '*asd231__dab': 2, '-2c**Ç21)=': 3})
        test_dict2 = collections.OrderedDict(
            {'a!a': {
                '-a**q231¨a': 1,
                'ab': {
                    ')(ab  as(a': 5}},
             'b': 2, 'c': 3, 'd(pepe)': {'da': 7}})

        result1 = normalize_dict(test_dict, exclusion=['_'])
        result2 = normalize_dict(test_dict2)

        self.assertEqual(result1, {'a-a': 1, 'asd231__dab': 2, '2c-c21': 3})
        self.assertEqual(result2, {
            'b': 2, 'a-a': {
                'ab': {'ab-as-a': 5},
                'a**q231-a': 1},
            'c': 3, 'd-pepe': {'da': 7}})

    def test_format_dict(self):
        """
        Test format_dict
        """
        test = {'a': 1, 'b': 2, 'c': 4}
        format_list = ['a', 'b', 'c']

        result = format_dict(test, format_list)
        format_list.reverse()
        result2 = format_dict(test, format_list, '*')

        self.assertEqual(result, '1,2,4')
        self.assertEqual(result2, '4*2*1')
