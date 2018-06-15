# -*- coding: utf-8 -*-
"""
Scrapbag csv file.
"""
import io
import csv
import codecs
import itertools
import collections
import xlrd
import structlog


from .strings import normalizer
from .collections import (exclude_empty_values, remove_list_duplicates,
                          force_list)
logger = structlog.getLogger(__name__)

# Output formats
ARRAY_RAW_FORMAT = 0
ARRAY_CLEAN_FORMAT = 1
DICT_FORMAT = 2


def get_csv_col_headers(rows, row_headers_count_value=0):
    """
    Retrieve csv column headers
    """
    count = 0

    if rows:
        for row in rows:
            if exclude_empty_values(row[:row_headers_count_value]):
                break
            count += 1

    if len(rows) == count:
        count = 1  # by default

    return [r[row_headers_count_value:] for r in rows[:count]]


def row_headers_count(rows):
    """
    Count the row headers in rows
    """
    count = 0

    if rows:
        for data in rows[0]:
            if not data:
                count += 1
            else:
                break
    return count


def populate_csv_headers(rows,
                         partial_headers,
                         column_headers_count=1):
    """
    Populate csv rows headers when are empty, extending the superior or
    upper headers.
    """

    result = [''] * (len(rows) - column_headers_count)

    for i_index in range(0, len(partial_headers)):
        for k_index in range(0, len(partial_headers[i_index])):

            # missing field find for a value in upper rows
            if not partial_headers[i_index][k_index] and i_index - 1 >= 0:

                # TODO: It's necesary a for or only taking the
                # inmediate latest row works well??
                for t_index in range(i_index - 1, -1, -1):
                    # TODO: could suposse that allways a value exists
                    partial_value = partial_headers[t_index][k_index]
                    if partial_value:
                        partial_headers[i_index][k_index] = partial_value
                        break

        result[i_index] = " ".join(map(str, partial_headers[i_index]))

    return result


def get_row_headers(rows, row_headers_count_value=0, column_headers_count=1):
    """
    Return row headers.
    Assume that by default it has one column header.
    Assume that there is only one father row header.
    """
    # TODO: REFACTOR ALGORITHM NEEDED
    partial_headers = []

    if row_headers_count_value:

        # Take partial data
        for k_index in range(0, len(rows) - column_headers_count):
            header = rows[k_index + column_headers_count][
                :row_headers_count_value]
            partial_headers.append(remove_list_duplicates(force_list(header)))

        # Populate headers
        populated_headers = populate_csv_headers(
            rows,
            partial_headers,
            column_headers_count)

        return populated_headers


def retrieve_csv_data(rows, row_header=0, column_header=0, limit_column=0):
    """
    Take the data from the rows.
    """
    return [row[row_header:limit_column] for row in rows[column_header:]]


def csv_tolist(path_to_file, **kwargs):
    """
    Parse the csv file to a list of rows.
    """

    result = []

    encoding = kwargs.get('encoding', 'utf-8')
    delimiter = kwargs.get('delimiter', ',')
    dialect = kwargs.get('dialect', csv.excel)

    _, _ext = path_to_file.split('.', 1)

    try:

        file = codecs.open(path_to_file, 'r', encoding)
        items_file = io.TextIOWrapper(file, encoding=encoding)
        result = list(
            csv.reader(items_file, delimiter=delimiter, dialect=dialect))

        items_file.close()
        file.close()

    except Exception as ex:
        result = []
        logger.error('Fail parsing csv to list of rows - {}'.format(ex))

    return result


def excel_todictlist(path_to_file, **kwargs):
    """
    Parse excel file to a dict list of sheets, rows.
    """
    result = collections.OrderedDict()
    encoding = kwargs.get('encoding', 'utf-8')
    formatting_info = '.xlsx' not in path_to_file
    count = 0

    with xlrd.open_workbook(
        path_to_file,
        encoding_override=encoding, formatting_info=formatting_info) \
            as _excelfile:

        for sheet_name_raw in _excelfile.sheet_names():

            # if empty sheet name put sheet# as name
            sheet_name = sheet_name_raw or "sheet{}".format(count)
            result[sheet_name] = []

            xl_sheet = _excelfile.sheet_by_name(sheet_name_raw)

            for row_idx in range(0, xl_sheet.nrows):
                col_data = []
                for col_idx in range(0, xl_sheet.ncols):

                    # Get cell object by row, col
                    cell_obj = xl_sheet.cell(row_idx, col_idx)
                    merged_info = is_merged(xl_sheet, row_idx, col_idx)

                    # Search for value in merged_info
                    if not cell_obj.value and merged_info:
                        cell_obj = search_mergedcell_value(
                            xl_sheet, merged_info[1])
                        col_data.append(cell_obj.value if cell_obj else '')
                    else:
                        col_data.append(cell_obj.value)

                result[sheet_name].append(col_data)

            count += 1  # increase sheet counter

    return result


def search_mergedcell_value(xl_sheet, merged_range):
    """
    Search for a value in merged_range cells.
    """
    for search_row_idx in range(merged_range[0], merged_range[1]):
        for search_col_idx in range(merged_range[2], merged_range[3]):
            if xl_sheet.cell(search_row_idx, search_col_idx).value:
                return xl_sheet.cell(search_row_idx, search_col_idx)
    return False


def is_merged(sheet, row, column):
    """
    Check if a row, column cell is a merged cell
    """
    for cell_range in sheet.merged_cells:
        row_low, row_high, column_low, column_high = cell_range
        if (row in range(row_low, row_high)) and \
                (column in range(column_low, column_high)):

            # TODO: IS NECESARY THIS IF?
            if ((column_high - column_low) < sheet.ncols - 1) and \
                    ((row_high - row_low) < sheet.nrows - 1):
                return (True, cell_range)

    return False


def populate_headers(headers):
    """
    Concatenate headers with subheaders
    """
    result = [''] * len(headers[0])
    values = [''] * len(headers)
    for k_index in range(0, len(headers)):
        for i_index in range(0, len(headers[k_index])):
            if headers[k_index][i_index]:
                values[k_index] = normalizer(
                    str(headers[k_index][i_index]))  # pass to str

            if len(exclude_empty_values(result)) > i_index:
                result[i_index] += "-{}".format(values[k_index])
            else:
                result[i_index] += str(values[k_index])

    return result


def row_csv_limiter(rows, limits=None):
    """
    Limit row passing a value or detect limits making the best effort.
    """

    limits = [None, None] if limits is None else limits

    if len(exclude_empty_values(limits)) == 2:
        upper_limit = limits[0]
        lower_limit = limits[1]
    elif len(exclude_empty_values(limits)) == 1:
        upper_limit = limits[0]
        lower_limit = row_iter_limiter(rows, 1, -1, 1)
    else:
        upper_limit = row_iter_limiter(rows, 0, 1, 0)
        lower_limit = row_iter_limiter(rows, 1, -1, 1)

    return rows[upper_limit: lower_limit]


def row_iter_limiter(rows, begin_row, way, c_value):
    """
    Alghoritm to detect row limits when row have more that one column.
    Depending the init params find from the begin or behind.
    NOT SURE THAT IT WORKS WELL..
    """
    limit = None

    for index in range(begin_row, len(rows)):
        if not len(exclude_empty_values(rows[way * index])) == 1:
            limit = way * index + c_value if way * index + \
                c_value not in [way * len(rows), 0] else None
            break

    return limit


def csv_row_cleaner(rows):
    """
    Clean row checking:
     - Not empty row.
     - >=1 element different in a row.
     - row allready in cleaned row result.


    """
    result = []

    for row in rows:

        # check not empty row
        check_empty = len(exclude_empty_values(row)) > 1

        # check more or eq than 1 unique element in row
        check_set = len(set(exclude_empty_values(row))) > 1
        # check row not into result cleaned rows.
        check_last_allready = (result and result[-1] == row)

        if check_empty and check_set and not check_last_allready:
            result.append(row)
    return result


def csv_column_cleaner(rows):
    """
    clean csv columns parsed omitting empty/dirty rows.
    """

    # check columns if there was empty columns
    result = [[] for x in range(0, len(rows))]
    for i_index in range(0, len(rows[0])):

        partial_values = []

        for x_row in rows:
            partial_values.append(
                x_row[i_index] if len(x_row) > i_index else '')

        colum_rows = exclude_empty_values(partial_values)

        if len(colum_rows) > len(rows) / 5:  # adjust this value
            for index in range(0, len(rows)):
                result[index].append(
                    rows[index][i_index] if len(rows[index]) > i_index else '')
    return result


def csv_column_header_cleaner(rows):
    """
    Clean column headers rows excluding empty values.
    """
    return exclude_empty_values(rows)


def csv_dict_format(csv_data, c_headers=None, r_headers=None):
    """
    Format csv rows parsed to Dict.
    """
    # format dict if has row_headers
    if r_headers:
        result = {}
        for k_index in range(0, len(csv_data)):
            if r_headers[k_index]:
                result[r_headers[k_index]] = collections.OrderedDict(
                    zip(c_headers, csv_data[k_index]))

    # format list if hasn't row_headers -- square csv
    else:
        result = []
        for k_index in range(0, len(csv_data)):
            result.append(
                collections.OrderedDict(zip(c_headers, csv_data[k_index])))
        result = [result]

    return result


def csv_array_clean_format(csv_data, c_headers=None, r_headers=None):
    """
    Format csv rows parsed to Array clean format.
    """

    result = []
    real_num_header = len(force_list(r_headers[0])) if r_headers else 0
    result.append([""] * real_num_header + c_headers)

    for k_index in range(0, len(csv_data)):

        if r_headers:
            result.append(
                list(
                    itertools.chain(
                        [r_headers[k_index]],
                        csv_data[k_index])))

        else:
            result.append(csv_data[k_index])

    return result


def csv_format(csv_data, c_headers=None, r_headers=None, rows=None, **kwargs):
    """
    Format csv rows parsed to Dict or Array
    """
    result = None
    c_headers = [] if c_headers is None else c_headers
    r_headers = [] if r_headers is None else r_headers
    rows = [] if rows is None else rows

    result_format = kwargs.get('result_format', ARRAY_RAW_FORMAT)

    # DICT FORMAT
    if result_format == DICT_FORMAT:
        result = csv_dict_format(csv_data, c_headers, r_headers)

    # ARRAY_RAW_FORMAT
    elif result_format == ARRAY_RAW_FORMAT:
        result = rows

    # ARRAY_CLEAN_FORMAT
    elif result_format == ARRAY_CLEAN_FORMAT:
        result = csv_array_clean_format(csv_data, c_headers, r_headers)

    else:
        result = None

    # DEFAULT
    if result and result_format < DICT_FORMAT:
        result = [result]

    return result


def csv_to_dict(csv_filepath, **kwargs):
    """
    Turn csv into dict.
    Args:
        :csv_filepath: path to csv file to turn into dict.
        :limits: path to csv file to turn into dict
    """
    callbacks = {'to_list': csv_tolist,
                 'row_csv_limiter': row_csv_limiter,
                 'csv_row_cleaner': csv_row_cleaner,
                 'row_headers_count': row_headers_count,
                 'get_col_header': get_csv_col_headers,
                 'get_row_headers': get_row_headers,
                 'populate_headers': populate_headers,
                 'csv_column_header_cleaner': csv_column_header_cleaner,
                 'csv_column_cleaner': csv_column_cleaner,
                 'retrieve_csv_data': retrieve_csv_data}

    callbacks.update(kwargs.get('alt_callbacks', {}))
    rows = kwargs.get('rows', [])

    if not rows:
        # csv_tolist of rows
        rows = callbacks.get('to_list')(csv_filepath, **kwargs)

        if not rows:
            msg = 'Empty rows obtained from {}'.format(csv_filepath)
            logger.warning(msg)
            raise ValueError(msg)

    # apply limits
    rows = callbacks.get('row_csv_limiter')(
        rows, kwargs.get('limits', [None, None]))

    # apply row cleaner
    rows = callbacks.get('csv_row_cleaner')(rows)

    # apply column cleaner
    rows = callbacks.get('csv_column_cleaner')(rows)

    # count raw headers
    num_row_headers = callbacks.get('row_headers_count')(rows)

    # take colum_headers
    c_headers_raw = callbacks.get('get_col_header')(rows, num_row_headers)

    # get row_headers
    r_headers = callbacks.get('get_row_headers')(
        rows, num_row_headers, len(c_headers_raw))

    # format colum_headers
    c_headers_dirty = callbacks.get('populate_headers')(
        c_headers_raw) if len(c_headers_raw) > 1 else c_headers_raw[0]

    # Clean csv column headers of empty values.
    c_headers = callbacks.get('csv_column_header_cleaner')(c_headers_dirty)

    # take data
    csv_data = callbacks.get('retrieve_csv_data')(
        rows,
        column_header=len(c_headers_raw),
        row_header=num_row_headers,
        limit_column=len(c_headers) - len(c_headers_dirty) or None)

    # Check column headers validation
    if csv_data:
        assert len(c_headers) == len(csv_data[0])

    # Check row headers validation
    if r_headers:
        assert len(r_headers) == len(csv_data)

    # Transform rows into dict zipping the headers.
    kwargs.pop('rows', None)
    result = csv_format(csv_data, c_headers, r_headers, rows, **kwargs)

    return result


def excel_to_dict(excel_filepath, encapsulate_filepath=False, **kwargs):
    """
    Turn excel into dict.
    Args:
        :excel_filepath: path to excel file to turn into dict.
        :limits: path to csv file to turn into dict
    """
    result = {}
    try:
        callbacks = {'to_dictlist': excel_todictlist}  # Default callback
        callbacks.update(kwargs.get('alt_callbacks', {}))

        # Retrieve excel data as dict of sheets lists
        excel_data = callbacks.get('to_dictlist')(excel_filepath, **kwargs)
        for sheet in excel_data.keys():
            try:
                kwargs['rows'] = excel_data.get(sheet, [])
                result[sheet] = csv_to_dict(excel_filepath, **kwargs)
            except Exception as ex:
                logger.error('Fail to parse sheet {} - {}'.format(sheet, ex))
                result[sheet] = []
                continue

        if encapsulate_filepath:
            result = {excel_filepath: result}

    except Exception as ex:
        msg = 'Fail transform excel to dict - {}'.format(ex)
        logger.error(msg, excel_filepath=excel_filepath)

    return result
