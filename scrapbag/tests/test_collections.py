# -*- coding: utf-8 -*-
"""
Test Scrapbag collection file
"""
import unittest
from collections import OrderedDict
from scrapbag.collections import (

    exclude_values,
    exclude_empty_values,
    check_fields,
    chunks,
    get_element,
    add_element,
    find_value_in_object,
    force_list,
    simplify_collection,
    flatten,
    merge_dicts,
    nested_dict_to_list,
    remove_list_duplicates,
    dict2orderedlist,
    get_dimension,
    get_ldict_keys,
    get_alldictkeys,
    clean_dictkeys,
    )


class UtilsCollectionsTestCase(unittest.TestCase):
    """
    Test Collection utils test case.
    """

    obj = {
        'a': 'a1',
        'aa': None,
        'b': ['b1', 'b2'],
        'c': ['c1', 'c2', 'c3'],
        'd': 'd1',
        'e': 'e1',
        'f': [{'f1': 'ff1', 'f2': 'ff2', 'g': 'ff3'}],
        'g': 'g1'
    }

    # ###### Manipulate collections functions ############################

    def test_exclude_values(self):
        """
        Test exclude_values
        """
        values = [None, [], '']
        original = {
            'a': None,
            'b': [],
            'c': '',
            'd': False,
            'e': 0,
            'f': [
                {},
                {'fa': 1, 'fb': []}],
        }

        empty_values_filter = exclude_values([], original)
        self.assertEqual(original, empty_values_filter)

        filtered = exclude_values(values, original)
        filtered2 = exclude_empty_values(original)
        self.assertEqual(len(filtered), 3)
        self.assertEqual(len(filtered), len(filtered2))
        self.assertNotEqual(filtered.get('f', {}), filtered2.get('f', {}))
        self.assertEqual(len(filtered.get('f', {})), 2)
        self.assertEqual(len(filtered2.get('f', {})), 1)

    def test_check_fields(self):
        """
        Test check_fields
        """
        fields = ('year', 'month', 'day')
        self.assertTrue(check_fields(
            fields, {'day': 1, 'year': 2014, 'month': 1}))

        self.assertFalse(check_fields(
            fields, {'day': 1, 'month': 1}))

    def test_get_element(self):
        """
        Test get_element
        """
        self.assertEqual(get_element(None, ''), None)
        self.assertEqual(get_element({'start': {'day': 1, }}, 'start/day'), 1)
        self.assertEqual(get_element({'start': {'day': 1, }}, 'start.day'), 1)
        self.assertEqual(get_element(
            {'start': {'day': 1, }}, 'start.'), {'day': 1, })
        self.assertEqual(
            get_element({'start': {'day': 1, }}, 'start.maria'), None)
        self.assertEqual(get_element(
            {'start': {'day': {'name': "Monday", 'num': 1}, }},
            'start/day.num'), 1)
        self.assertEqual(get_element({'start': [0, 1, 2]}, 'start.1'), 1)

    def test_add_element(self):
        """
        Test add_element
        """
        self.assertEqual(add_element(None, '', None), False)

        result = {}
        self.assertEqual(add_element(result, 'a', 1), {'a': 1})
        self.assertEqual(result.get('a'), 1)
        self.assertEqual(len(result.keys()), 1)

        # a is not a dict...
        self.assertEqual(add_element(result, 'a.aa', 2),  {'a': {'aa': 2}})

        # the separator keys not retrieve anything or empty path apply the
        # separator expr.
        self.assertEqual(add_element(result, '', 2, r'-'), result)

        # TEST navigate and create a key - value
        result['a'] = {}

        self.assertEqual(add_element(result, 'a.aa', 2), {'a': {'aa': 2}})
        self.assertEqual(result.get('a', {}).get('aa'), 2)
        self.assertEqual(len(result.get('a').keys()), 1)

        self.assertEqual(add_element(result, 'a.ab', 3),
                         {'a': {'aa': 2, 'ab': 3}})
        self.assertEqual(result.get('a', {}).get('aa'), 2)
        self.assertEqual(result.get('a', {}).get('ab'), 3)
        self.assertEqual(len(result.get('a').keys()), 2)

        # TEST Add to list
        result['a']['aa'] = []

        self.assertEqual(add_element(result, 'a.aa', 2),
                         {'a': {'aa': [2], 'ab': 3}})
        self.assertEqual(add_element(result, 'a.aa', 4),
                         {'a': {'aa': [2, 4], 'ab': 3}})

        self.assertEqual(add_element({'a': [1, 3]}, 'a.1', 2, override=False, digit=True), {'a': [1, 3, 2]})

        self.assertEqual(add_element({'a': [1, 3]}, 'a.1', 2, override=True, digit=True), {'a': [1, 2]})

        # fail override mode not activated and a.1 element is not a list.
        self.assertEqual(add_element(
            {'a': [1, 3]}, 'a.1', 2, override=True),
            {'a': [1, 2]})
        self.assertEqual(add_element(
            {'a': [1, 3]}, 'a.1', 2, override=False),
            {'a': [1, 3, 2]})
        self.assertEqual(add_element(
            {'a': [1, 3]}, 'a.1.0', 2),
            {'a': [1, [2]]})

        self.assertEqual(add_element(
            {'a': [1, 3]}, 'a.1.0', 2, override=True),
            {'a': [1, [2]]})

        self.assertEqual(add_element(
            {'a': [1, 3]}, 'a.1.test', 2, override=True),
            {'a': [1, {'test': 2}]})

        self.assertEqual(add_element(
            {'a': [1, 3]}, 'a.1.test.0', 2, override=True),
            {'a': [1, {'test': [2]}]})

        self.assertEqual(add_element(
            {'a': [1, 3]}, 'a.1.test.0', 2, digit=False, override=True),
            {'a': {'1': {'test': {'0': 2}}}})

        self.assertEqual(
            add_element({'a': [1, 3]}, 'a.1.test.1', 2, override=True),
            {'a': [1, {'test': ["", 2]}]})

        self.assertEqual(add_element(
            {'a': [1, {'test': [2]}]}, 'a.1.test.1', 3),
            {'a': [1, {'test': [2, 3]}]})

        self.assertEqual(
            add_element({'a': [1, {'test': [2]}]}, 'a.2.test.1', 3),
            {'a': [1, {'test': [2]}, {'test': ["", 3]}]})

        # TEST Add to dict
        result['a']['aa'] = {}

        self.assertEqual(
            add_element(result, 'a.aa', {'aaa': 2}),
            {'a': {'aa': {'aaa': 2}, 'ab': 3}})

        self.assertEqual(
            add_element(result, 'a.aa', {'aab': 3}),
            {'a': {'aa': {'aaa': 2, 'aab': 3}, 'ab': 3}})

    def test_find_value_in_nested_dict(self):
        """
        Test find_value_in_nested_dict
        """
        self.assertEqual(
            list(find_value_in_object('g', self.obj)), ['g1', 'ff3'])
        self.assertEqual(
            list(find_value_in_object('c', self.obj)), ['c1', 'c2', 'c3'])

    def test_force_list(self):
        """
        Test force_list
        """
        result = force_list(None)
        self.assertEqual(result, [])

        result = force_list([])
        self.assertEqual(result, [])

        result = force_list(['casa'])
        self.assertEqual(result, ['casa'])

        result = force_list('casa')
        self.assertEqual(result, ['casa'])

    def test_simplify_collection(self):

        test1 = ['', 1, [], None]
        test2 = ['', [1, ''], None, [2, None, '', 3]]
        test3 = ['', (3, ''), (None)]
        test4 = {'a': [], 'b': 2, 'c': [1, [], None, {}]}

        test5 = [[[1, 2, 3]]]

        self.assertEqual(simplify_collection(None), None)

        self.assertEqual(simplify_collection(test1), 1)
        self.assertEqual(simplify_collection(test2), [1, [2, 3]])
        self.assertEqual(simplify_collection(test3), (3, ''))
        self.assertEqual(simplify_collection(test4), {'b': 2, 'c': 1})
        self.assertEqual(
            simplify_collection(test4, True, ),
            {'b': 2, 'c': [1]})

        self.assertEqual(simplify_collection(test5), [1, 2, 3])

    def test_chunks(self):

        self.assertEqual(len([x for x in chunks([1, 2, 3, 4, 5], 2)]), 3)
        self.assertEqual(len([x for x in chunks([1, 2, 3, 4, 5], 100)]), 1)
        self.assertEqual([x for x in chunks({'test': 2}, 4)], [])

    def test_flatten(self):
        """
        Test flatten
        """
        test = OrderedDict(
            {'a': 2,
             'b': 2,
             'c': {'ca': 3, 'cb': 'test1', 'cd': [1, 3, 4], 'cc': {'cca': 1}}})

        test2 = [
            test,
            {'x': 4, 'y': 5},
            {'z': {'za': 6}}

        ]

        test3 = {'a': [
                {'aa': {'aaa': [1, 2, 3]},
                 'ab': {'aba': [1, 2, 3]},
                 'ac': {'aca': [1, 2, 3]}}
                 ]}

        test_result_1a = OrderedDict([
            ('a', 2),
            ('b', 2),
            ('c/ca', 3),
            ('c/cb', test.get('c', {}).get('cb')),
            ('c/cc/cca', 1),
            ('c/cd/1', 3),
            ('c/cd/0', 1),
            ('c/cd/2', 4)])

        test_result_1b = OrderedDict([
            ('test_a', 2),
            ('test_c_ca', 3),
            ('test_c_cd_1', 3),
            ('test_c_cd_2', 4),
            ('test_c_cd_0', 1),
            ('test_c_cb', test.get('c', {}).get('cb')),
            ('test_c_cc_cca', 1),
            ('test_b', 2)])

        test_result_2a = OrderedDict([
            ('0/a', 2),
            ('0/c/ca', 3),
            ('0/c/cb', 'test1'),
            ('0/c/cc/cca', 1),
            ('0/c/cd/0', 1),
            ('0/c/cd/2', 4),
            ('0/c/cd/1', 3),
            ('0/b', 2),
            ('2/z/za', 6),
            ('1/x', 4),
            ('1/y', 5)])

        test_result_2b = OrderedDict([
            ('test_0_a', 2),
            ('test_0_c_ca', 3),
            ('test_0_c_cb', 'test1'),
            ('test_0_c_cc_cca', 1),
            ('test_0_c_cd_0', 1),
            ('test_0_c_cd_2', 4),
            ('test_0_c_cd_1', 3),
            ('test_0_b', 2),
            ('test_2_z_za', 6),
            ('test_1_x', 4),
            ('test_1_y', 5)])

        test_result_3a = OrderedDict([
            ('a/0/ac/aca/0', 1),
            ('a/0/ac/aca/2', 3),
            ('a/0/ac/aca/1', 2),
            ('a/0/ab/aba/0', 1),
            ('a/0/ab/aba/2', 3),
            ('a/0/ab/aba/1', 2),
            ('a/0/aa/aaa/0', 1),
            ('a/0/aa/aaa/2', 3),
            ('a/0/aa/aaa/1', 2)])

        test_result_3b = OrderedDict([
            ('test_a_0_ac_aca_0', 1),
            ('test_a_0_ac_aca_2', 3),
            ('test_a_0_ac_aca_1', 2),
            ('test_a_0_ab_aba_0', 1),
            ('test_a_0_ab_aba_2', 3),
            ('test_a_0_ab_aba_1', 2),
            ('test_a_0_aa_aaa_0', 1),
            ('test_a_0_aa_aaa_2', 3),
            ('test_a_0_aa_aaa_1', 2)])

        # results of test 1
        result_1a = flatten(test, '', sep='/')
        result_1b = flatten(test, 'test')

        # results of test 2
        result_2a = flatten(test2, '', sep='/')
        result_2b = flatten(test2, 'test')

        # results of test 3
        result_3a = flatten(test3, '', sep='/')
        result_3b = flatten(test3, 'test')

        for retrieved_result, test_result in [
            (result_1a, test_result_1a),
            (result_1b, test_result_1b),
            (result_2a, test_result_2a),
            (result_2b, test_result_2b),
            (result_3a, test_result_3a),
            (result_3b, test_result_3b)
        ]:

            for key, value in test_result.items():
                self.assertIn(key, retrieved_result)
                self.assertEqual(retrieved_result[key], value)

        self.assertEqual(flatten('test'), 'test')

    def test_merge_dicts(self):

        self.assertEqual(merge_dicts({}, {'a': 1}), {'a': 1})

        self.assertEqual(merge_dicts({'a': 2}, {'a': 1}), {'a': 1})

        self.assertEqual(merge_dicts({'a': {'aa': 1}}, {'a': {'ab': 2}}), {'a': {'aa': 1, 'ab': 2}})

        self.assertEqual(merge_dicts({'a': {'aa': [3]}}, {'a': {'aa': 5}}, digit=False), {'a': {'aa': [3, 5]}})

        self.assertEqual(merge_dicts({'a': {'aa': [3]}}, {'a': {'aa': {'1': 5}}}, digit=True), {'a': {'aa': [3, 5]}})

        self.assertEqual(merge_dicts({'a': {'aa': [3]}}, {'a': {'aa': [5]}}, override=False, digit=True), {'a': {'aa': [3, 5]}})

        self.assertEqual(merge_dicts({'a': {'aa': [3]}}, {'a': {'aa': [5]}}, override=True, digit=True), {'a': {'aa': [5]}})


        # bad arguments not dicts
        self.assertEqual(merge_dicts([], {'a': 1}), {})
        self.assertEqual(merge_dicts([], []), {})
        self.assertEqual(merge_dicts({'a': 1}, []), {})

    def test_nested_dict_to_list(self):
        """
        Test nested_dict_to_list
        """
        expected = [
            ['', 'b', 'bv2'],
            ['', 'a', 'av1'],
            ['c', 'cc', 'ccv1'],
            ['c', 'ca', 'cav1'],
            ['c', 'cb', 'cbv1'],
            ['ccca', 'ccaa', 'ccaav1']]

        test = OrderedDict([
            ('b', 'bv2'),
            ('a', 'av1'),
            ('c', OrderedDict([
                ('cc', 'ccv1'),
                ('ca', 'cav1'),
                ('cb', 'cbv1'),
                ('cca', OrderedDict([
                    ('ccaa', 'ccaav1')])),
            ]))])

        result = nested_dict_to_list("", test)
        result_exclusion = nested_dict_to_list("", test, exclusion=['c'])

        self.assertEqual(
            all(row_result in expected for row_result in result), True)
        self.assertEqual(len(result), len(expected))

        check = (row_result in expected[:2] for row_result in result_exclusion)

        self.assertEqual(all(check), True)

        self.assertEqual(len(result_exclusion), len(expected[:2]))

    def test_remove_duplicates(self):
        """
        Test remove_duplicates
        """

        expected = [[1], [2, 1, 3], [2, 1, 5], [5], [88]]
        expected1 = [[2, 1, 3], [2, 1, 5], [5], [88]]
        lista = [[1], [2, 1, 3], [1], [2, 1, 5], [5], [88], [1]]

        result = remove_list_duplicates(lista)
        result1 = remove_list_duplicates(lista, unique=True)

        self.assertEqual(result, expected)
        self.assertEqual(result1, expected1)

    def test_dict2orderedlist(self):
        """
        Test dict2orderedlist
        """

        test_dict = {'a': 1, 'b': 2, 'c': 3}
        test_flatten = {'a': 1, 'b': {'ba': 2}, 'c': 3}

        result1 = dict2orderedlist(test_dict, ['a', 'b', 'c'])
        result2 = dict2orderedlist(test_dict, ['a', 'c'])
        result3 = dict2orderedlist(test_dict, ['c', 'b', 'a'])
        result4 = dict2orderedlist(
            test_flatten, ['c', 'b.ba', 'a', 'x'], default='test')

        self.assertEqual(result1, [1, 2, 3])
        self.assertEqual(result2, [1, 3])
        self.assertEqual(result3, [3, 2, 1])
        self.assertEqual(result4, [3, 2, 1, 'test'])

    def test_get_dimension(self):
        """
        Test get_dimension
        """

        test = [1, 2, 3]
        test2 = [test, test, test]
        test3 = [test2, test, test2]
        test4 = {'a': 1, 'b': 2, 'c': 3}
        bad_test = "bad_test"

        result1 = get_dimension(test)
        result2 = get_dimension(test2)
        result3 = get_dimension(test3)
        result4 = get_dimension(test4)
        result_bad_test = get_dimension(bad_test)

        self.assertEqual(result1, [3, 1])
        self.assertEqual(result2, [3, 3])
        self.assertEqual(result3, [3, 3])  # could need a fix this case..
        self.assertEqual(result4, [1, 3])
        self.assertEqual(result_bad_test, [0, 0])

    def test_get_ldict_keys(self):
        """
        Test get ldictkeys
        """
        test = [{'a': 2}, {'b': 3}, ['test'], {'c': {'ca': 4, 'cb': 5}}]
        assert_result1 = ['a', 'b', 'c']
        assert_result2a = ['a', 'b', 'c_ca', 'c_cb']
        assert_result2b = ['a', 'b', 'c.ca', 'c.cb']

        result1 = get_ldict_keys(test)
        result2a = get_ldict_keys(test, flatten_keys=True)
        result2b = get_ldict_keys(test, flatten_keys=True, sep='.')

        self.assertEqual(all(x in result1 for x in assert_result1), True)
        self.assertEqual(len(result1), 3)

        self.assertEqual(all(x in result2a for x in assert_result2a), True)
        self.assertEqual(len(result2a), 4)
        self.assertEqual(all(x in result2b for x in assert_result2b), True)
        self.assertEqual(len(result2b), 4)

    def test_get_alldictkeys(self):
        """
        Test get_alldictkeys
        """

        test = {'a': 1, 'b': 2, 'c': {'ca': 3, 'cb': 4}}
        test2 = ['a', 'b', 'c']

        assert_result1 = [('c', 'ca'), ('c', 'cb'), ('a',), ('b',)]
        result1 = get_alldictkeys(test)
        result2 = get_alldictkeys(test2)

        self.assertEqual(all(x in result1 for x in assert_result1), True)
        self.assertEqual(len(result1), 4)
        self.assertEqual(result2, [()])

    def test_clean_dictkeys(self):
        """
        Test clean_dictkeys
        """

        test = OrderedDict({
            'a': 1,
            'b': 2,
            'c': {
                'ca': 3,
                'cb': 4,
                'cd': 5},
            'd': [1, 2, {'dda': 6, 'dd': 7}]})

        result1 = clean_dictkeys([])
        assert_result1 = {}

        result2 = clean_dictkeys(test)
        assert_result2 = test

        result3 = clean_dictkeys(test, ['a'])
        assert_result3 = OrderedDict({
            'b': 2,
            'c': {
                'c': 3,
                'cb': 4,
                'cd': 5},
            'd': [1, 2, {
                'dd': [6, 7]}]})

        test = OrderedDict({
            'a': 1,
            'b': 2,
            'c': {
                'ca': 3,
                'cb': 4,
                'cd': 5},
            'd': [1, 2, {'dda': 6, 'dd': 7}]})

        result4 = clean_dictkeys(test, ['a', 'b'])
        assert_result4 = OrderedDict(
            {'c': {'c': [3, 4], 'cd': 5, }, 'd': [1, 2, {'dd': [6, 7]}]})

        self.assertEqual(result1, assert_result1)
        self.assertEqual(result2, assert_result2)
        self.assertEqual(
            sorted(flatten(dict(result3)).keys()),
            sorted(flatten(assert_result3).keys())
        )

        self.assertEqual(
            sorted(flatten(dict(result4)).keys()),
            sorted(flatten(assert_result4).keys())
        )
