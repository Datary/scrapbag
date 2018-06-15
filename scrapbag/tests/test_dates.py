# -*- coding: utf-8 -*-
"""
Test Scrapbag dates file
"""
import unittest
from datetime import datetime, timedelta
from scrapbag.dates import (
    get_dates_in_period,
    ordinal_suffix,
    localize_date,
    get_year_from_date_str,
    get_month_from_date_str,
    replace_month_abbr_with_num,
    translate_month_abbr,
    merge_datetime
    )


class UtilsDatesTestCase(unittest.TestCase):
    """
    Scrapbag dates Test Case
    """

    def test_get_dates_in_period(self):
        """
        Test get_dates_in_period
        """

        test = get_dates_in_period()
        self.assertEqual(len(test), 2)

        test_same = get_dates_in_period(start=datetime.today(), top=datetime.today())
        self.assertEqual(len(test_same), 1)
        self.assertEqual(test_same[0].date(), datetime.today().date())

        test_1_30 = get_dates_in_period(step=30)
        self.assertEqual(len(test_1_30), 2)

        test_1_month = get_dates_in_period(step_dict={'months': 1})
        self.assertEqual(len(test_1_month), 2)

        test_30 = get_dates_in_period(top=datetime.today() + timedelta(days=30), step=1)

        # default return a list of next 30 days from today
        self.assertEqual(len(test_30), 30)
        self.assertEqual(test_30[0].date(), datetime.today().date())
        self.assertEqual(
            test_30[-1].date(), (datetime.today() + timedelta(days=30-1)).date())

        test_100 = get_dates_in_period(start=datetime.today() + timedelta(days=50), step=50)

        self.assertEqual(len(test_100), 2)

        self.assertEqual(
            test_100[0].date(), (datetime.today() + timedelta(days=50)).date())

        self.assertEqual(
            test_100[1].date(), (datetime.today() + timedelta(days=100)).date())

        test_2 = get_dates_in_period(
            top=datetime.today() + timedelta(days=6), step=2)

        self.assertEqual(len(test_2), 3)

        for index in range(0, 3):
            self.assertEqual(
                test_2[index].date(),
                (datetime.today() + timedelta(days=2*index)).date())

    def test_ordinal_suffix(self):
        """
        Test ordinal_suffix
        """

        self.assertEqual(ordinal_suffix(1), 'st')
        self.assertEqual(ordinal_suffix(2), 'nd')
        self.assertEqual(ordinal_suffix(3), 'rd')
        self.assertEqual(ordinal_suffix(4), 'th')
        self.assertEqual(ordinal_suffix(24), 'th')

    def test_localize_date(self):
        """
        Test localize_date
        """

        test_date = datetime.now()

        canarias = localize_date(test_date, 'Atlantic/Canary')
        madrid = localize_date(test_date, 'Europe/Madrid')
        berlin = localize_date(test_date, 'Europe/Berlin')

        self.assertEqual(canarias.tzname() != madrid.tzname(), True)
        self.assertEqual(berlin.tzname(), madrid.tzname())

    def test_get_year_from_date_str(self):
        """
        Test get_year_from_date_str
        """

        result = get_year_from_date_str('marzo 1991 lalal')
        result2 = get_year_from_date_str('marzo1991lalal')
        result_bad = get_year_from_date_str('marzo199lalal')
        result_bad2 = get_year_from_date_str('marzolalal')

        self.assertEqual(result, result2)
        self.assertEqual(result, ['1991'])
        self.assertEqual(result_bad, [])
        self.assertEqual(result_bad, result_bad2)

    def test_get_month_from_date_str(self):
        """
        Test get_month_from_date_str
        """

        self.assertEqual(get_month_from_date_str(
            '5 de marzo de 2017', 'es'), (3, 'mar'))
        self.assertEqual(get_month_from_date_str(
            '5 de march de 2017', 'en'), (3, 'Mar'))
        self.assertEqual(
            get_month_from_date_str('5 de ma123o de 2017', 'en'), ())

    def test_replace_month_abbr_num(self):
        """
        Test replace_month_abbr_num
        """

        self.assertEqual(replace_month_abbr_with_num(
            '10-ene-2013', lang="es"), '10-1-2013')
        self.assertEqual(replace_month_abbr_with_num(
            '11-feb-2012', lang="es"), '11-2-2012')
        self.assertEqual(replace_month_abbr_with_num(
            '12-mar-2011', lang="es"), '12-3-2011')
        self.assertEqual(replace_month_abbr_with_num(
            '13-abr-2010', lang="es"), '13-4-2010')
        self.assertEqual(replace_month_abbr_with_num(
            '14-may-2009', lang="es"), '14-5-2009')
        self.assertEqual(replace_month_abbr_with_num(
            '15-jun-2008', lang="es"), '15-6-2008')
        self.assertEqual(replace_month_abbr_with_num(
            '16-jul-2007', lang="es"), '16-7-2007')
        self.assertEqual(replace_month_abbr_with_num(
            '17-ago-2006', lang="es"), '17-8-2006')
        self.assertEqual(replace_month_abbr_with_num(
            '18-sep-2005', lang="es"), '18-9-2005')
        self.assertEqual(replace_month_abbr_with_num(
            '19-oct-2004', lang="es"), '19-10-2004')
        self.assertEqual(replace_month_abbr_with_num(
            '20-nov-2003', lang="es"), '20-11-2003')
        self.assertEqual(replace_month_abbr_with_num(
            '21-dic-2002', lang="es"), '21-12-2002')
        self.assertEqual(replace_month_abbr_with_num(
            'Apr 23, 2002', lang="en"), '4 23, 2002')

    def test_translate_month_abbr(self):
        """
        Test translate_month_abbr
        """
        test_date_str = '12-ene-2013'

        with self.assertRaises(Exception):
            translate_month_abbr(test_date_str, 'test', 'en')

        with self.assertRaises(Exception):
            translate_month_abbr(test_date_str, 'es', 'test')

        result = translate_month_abbr(test_date_str, 'es', 'en')
        self.assertEqual(result, '12-Jan-2013')
        self.assertEqual(translate_month_abbr(
            result, 'en', 'es'), test_date_str)

    def test_merge_datetime(self):
        """
        Test merge_datetime
        """
        test_datetime = "15/02/2017"
        test_datetime2 = "15-02-2017"
        test_time = "12:56"
        test_time2 = "22:56"

        result = merge_datetime(test_datetime, test_time)
        result2 = merge_datetime(
            test_datetime2, test_time2, date_format='%d-%m-%Y')
        result3 = merge_datetime(test_datetime)

        self.assertEqual(result, datetime(2017, 2, 15, 12, 56))
        self.assertEqual(result2, datetime(2017, 2, 15, 22, 56))
        self.assertEqual(result3, datetime(2017, 2, 15))
