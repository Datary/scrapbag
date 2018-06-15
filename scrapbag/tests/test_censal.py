# -*- coding: utf-8 -*-
"""
Test Scrapbag files file
"""
import unittest

from scrapbag.censal import IneCensal


class UtilsFilesTestCase(unittest.TestCase):

    def setUp(self):
        self.ine_censal = IneCensal()

    def test_get_codigo_censal(self):

        self.assertEqual(len(self.ine_censal.index_localidades), 8228)

        self.assertEqual(self.ine_censal.get_codigo_censal('madrid'), '28079')
        self.assertEqual(self.ine_censal.get_codigo_censal(['madrid', 'falsi_provincia']), '28079')

        self.assertEqual(self.ine_censal.get_codigo_censal('castejon'), None)
        self.assertEqual(self.ine_censal.get_codigo_censal(['castejon', 'navarra']), '31070')
        self.assertEqual(self.ine_censal.get_codigo_censal(['castejon', 'cuenca']), '16067')
        self.assertEqual(self.ine_censal.get_codigo_censal(['castejon', 'cu']), '16067')
        self.assertEqual(self.ine_censal.get_codigo_censal(['caste', 'cu']), None)

        self.assertEqual(self.ine_censal.get_codigo_censal(['burriana']), '12032')
        self.assertEqual(self.ine_censal.get_codigo_censal(['chilches']), '12053')

        self.assertEqual(self.ine_censal.get_codigo_censal(['Elche/Elx']), '03065')

        self.assertEqual(self.ine_censal.get_codigo_censal(['Elche/Elx']), '03065')

        self.assertEqual(self.ine_censal.get_codigo_censal(['La floresta'], force_check=True), '25092')
        self.assertEqual(self.ine_censal.get_codigo_censal(['La floresta', 'lleida'], force_check=True), '25092')
        self.assertEqual(self.ine_censal.get_codigo_censal(['La floresta', 'barcelona'], force_check=True), None)
        self.assertEqual(self.ine_censal.get_codigo_censal(['La floresta', 'barcelona'], force_check=False), '25092')

        self.assertEqual(self.ine_censal.get_codigo_censal(['cabanes', 'castellón/castello'], force_check=False), '12033')

        self.assertEqual(self.ine_censal.get_codigo_censal(['la solana', 'A coruña'], force_check=True), None)
        self.assertEqual(self.ine_censal.get_codigo_censal(['la solana', 'ciudad real', 'madrid'], force_check=True), None)
        self.assertEqual(self.ine_censal.get_codigo_censal(['la solana', 'ciudad real', 'castilla la mancha'], force_check=True), '13079')
