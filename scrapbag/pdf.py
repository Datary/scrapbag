# -*- coding: utf-8 -*-
"""
Scrapbag pdf file.
"""
import os
import logging
from io import StringIO

import pdfminer.layout
import pdfminer.settings
import pdfminer.high_level


import structlog

from .collections import exclude_empty_values

pdfminer.settings.STRICT = False
logging.getLogger('pdfminer').setLevel(logging.ERROR)

logger = structlog.getLogger(__name__)


def pdf_to_text(pdf_filepath='', **kwargs):
    """
    Parse pdf to a list of strings using the pdfminer lib.

    Args:
        no_laparams=False,
        all_texts=None,
        detect_vertical=None, word_margin=None, char_margin=None,
        line_margin=None, boxes_flow=None, codec='utf-8',
        strip_control=False, maxpages=0, page_numbers=None, password="",
        scale=1.0, rotation=0, layoutmode='normal', debug=False,
        disable_caching=False,
    """

    result = []
    try:
        if not os.path.exists(pdf_filepath):
            raise ValueError("No valid pdf filepath introduced..")

        # TODO: REVIEW THIS PARAMS
        # update params if not defined
        kwargs['outfp'] = kwargs.get('outfp', StringIO())
        kwargs['laparams'] = kwargs.get('laparams', pdfminer.layout.LAParams())
        kwargs['imagewriter'] = kwargs.get('imagewriter', None)
        kwargs['output_type'] = kwargs.get('output_type', "text")
        kwargs['codec'] = kwargs.get('codec', 'utf-8')
        kwargs['disable_caching'] = kwargs.get('disable_caching', False)

        with open(pdf_filepath, "rb") as f_pdf:
            pdfminer.high_level.extract_text_to_fp(f_pdf, **kwargs)

        result = kwargs.get('outfp').getvalue()

    except Exception:
        logger.error('fail pdf to text parsing')

    return result


def pdf_row_limiter(rows, limits=None, **kwargs):
    """
    Limit row passing a value. In this case we dont implementate a best effort
    algorithm because the posibilities are infite with a data text structure
    from a pdf.
    """
    limits = limits or [None, None]

    upper_limit = limits[0] if limits else None
    lower_limit = limits[1] if len(limits) > 1 else None

    return rows[upper_limit: lower_limit]


def pdf_row_format(row_str, **kwargs):
    """
    Retrieve formated pdf row by default as string.
    """
    return row_str


def pdf_row_parser(rows, **kwargs):
    """
    Retrieve rows parsed by default.
    """
    return rows


def pdf_row_cleaner(rows, **kwargs):
    """
    Check if there are any empty dict in the list of rows.
    """
    return exclude_empty_values(rows)


def pdf_to_dict(pdf_filepath, **kwargs):

    """
    Main method to parse a pdf file to a dict.
    """

    callbacks = {
        'pdf_to_text': pdf_to_text,
        'pdf_row_format': pdf_row_format,
        'pdf_row_limiter': pdf_row_limiter,
        'pdf_row_parser': pdf_row_parser,
        'pdf_row_cleaner': pdf_row_cleaner
        }

    callbacks.update(kwargs.get('alt_callbacks', {}))
    rows = kwargs.get('rows', [])

    if not rows:
        # pdf to string
        rows_str = callbacks.get('pdf_to_text')(pdf_filepath, **kwargs)

        # string to list of rows
        rows = callbacks.get('pdf_row_format')(rows_str, **kwargs)

    # apply limits
    rows = callbacks.get('pdf_row_limiter')(rows, **kwargs)

    # Parse data from rows to dict
    rows = callbacks.get('pdf_row_parser')(rows, **kwargs)

    # apply cleaner
    rows = callbacks.get('pdf_row_cleaner')(rows)

    return rows
