# -*- coding: utf-8 -*-
"""
Scrapbag dates file.
"""
import re
import locale
import calendar

from datetime import timedelta, datetime
from dateutil.relativedelta import relativedelta


import pytz
import structlog


logger = structlog.getLogger(__name__)

LOCALES = {
    "es": locale.normalize("es_ES.UTF-8"),
    "en": locale.normalize("en_US.UTF-8"),
    "fr": locale.normalize("fr_FR.UTF-8"),
    "de": locale.normalize("de_DE.UTF-8"),
    "it": locale.normalize("it_IT.UTF-8"),
}

DEFAULT_DATE_LANG = 'en'


def get_dates_in_period(start=None, top=None, step=1, step_dict={}):
    """Return a list of dates from the `start` to `top`."""

    delta = relativedelta(**step_dict) if step_dict else timedelta(days=step)

    start = start or datetime.today()
    top = top or start + delta
    dates = []
    current = start
    while current <= top:
        dates.append(current)
        current += delta
    return dates


def ordinal_suffix(day):
    """Return ordinal english suffix to number of a day."""
    condition = 4 <= day <= 20 or 24 <= day <= 30
    return 'th' if condition else ["st", "nd", "rd"][day % 10 - 1]


def localize_date(date, city):
    """ Localize date into city

    Date: datetime
    City: timezone city definitio. Example: 'Asia/Qatar', 'America/New York'..
    """
    local = pytz.timezone(city)
    local_dt = local.localize(date, is_dst=None)
    return local_dt


def get_year_from_date_str(date_str):
    """
    Retrieve only the year from a text string.
    """
    return re.findall(r'\d{4}', date_str) if date_str else None


def get_month_from_date_str(date_str, lang=DEFAULT_DATE_LANG):
    """Find the month name for the given locale, in the given string.

    Returns a tuple ``(number_of_month, abbr_name)``.
    """
    date_str = date_str.lower()
    with calendar.different_locale(LOCALES[lang]):
        month_abbrs = list(calendar.month_abbr)
        for seq, abbr in enumerate(month_abbrs):
            if abbr and abbr.lower() in date_str:
                return seq, abbr
    return ()


def replace_month_abbr_with_num(date_str, lang=DEFAULT_DATE_LANG):
    """Replace month strings occurrences with month number."""
    num, abbr = get_month_from_date_str(date_str, lang)
    return re.sub(abbr, str(num), date_str, flags=re.IGNORECASE)


def translate_month_abbr(
        date_str,
        source_lang=DEFAULT_DATE_LANG,
        target_lang=DEFAULT_DATE_LANG):
    """Translate the month abbreviation from one locale to another."""
    month_num, month_abbr = get_month_from_date_str(date_str, source_lang)
    with calendar.different_locale(LOCALES[target_lang]):
        translated_abbr = calendar.month_abbr[month_num]
        return re.sub(
            month_abbr, translated_abbr, date_str, flags=re.IGNORECASE)


def merge_datetime(date, time='', date_format='%d/%m/%Y', time_format='%H:%M'):
    """Create ``datetime`` object from date and time strings."""
    day = datetime.strptime(date, date_format)
    if time:
        time = datetime.strptime(time, time_format)
        time = datetime.time(time)
        day = datetime.date(day)
        day = datetime.combine(day, time)
    return day
