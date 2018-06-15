# -*- coding: utf-8 -*-
"""
Scrapbag spss file.
"""
import re
import codecs
import structlog

from .collections import exclude_empty_values, add_element, force_list
from .strings import get_only_words

logger = structlog.getLogger(__name__)


def parse_spss_header_leyend(raw_leyend, leyend={}, **kwargs):

    try:
        for raw_leyend_line in raw_leyend.split('/')[1].split('\r\n'):
            head = []

            for raw_value in raw_leyend_line.strip().split():

                clean_value = get_only_words(re.sub(r'\(.*\)', '', raw_value))

                if all([x.isdigit() for x in clean_value]):
                    str_head = " ".join(head)

                    # supossed that only questions uses TO
                    if ' TO ' in str_head:
                        id_range = list(map(int, re.findall(r'(\d+)', str_head)))
                        id_range[1] += 1

                        column_range = list(map(int, clean_value))
                        column_range[1] += 1

                        for i, column in zip(range(*id_range, 1), range(*column_range, 1)):
                            add_element(
                                leyend,
                                '{}/columns'.format("P{}".format(i)),
                                [column - 1, int(column)])

                    # More than one head waiting to assign leyend columns
                    elif len(head) > 1:

                        num_heads = len(head)

                        column_range = list(map(int, clean_value))
                        column_range[1] += 1
                        non_iter_column_range = [x for x in range(*column_range)]

                        offset = int(len(non_iter_column_range) / num_heads)

                        for head_i, column in zip(iter(head), range(*column_range, offset)):

                            add_element(
                                leyend,
                                '{}/columns'.format(head_i),
                                [column - 1, column + offset - 1] if offset != 1 else [column - 1, column])

                    # only one head
                    else:

                        list_clean_value = list(map(int, clean_value))

                        if len(list_clean_value) == 1:
                            list_clean_value.append(list_clean_value[0])

                        list_clean_value[0] -= 1

                        add_element(
                            leyend,
                            '{}/columns'.format(" ".join(head)),
                            list_clean_value
                            )

                    head = []

                else:
                    head.append(raw_value)

    except Exception as ex:
        logger.error('Fail to parse leyend - {}'.format(ex))

    return leyend


def parse_variable_label(raw_labels, headers):

    for label in [exclude_empty_values(x.strip().split("'")) for x in raw_labels]:
        try:
            add_element(
                headers,
                '{}/variable_label'.format(label[0].replace('/', '').strip()),
                label[1].strip())

        except Exception as ex:
            logger.error('Fail to parse variable label', label=label)


def parse_value_label(raw_labels, headers):

    heads = []
    raw_labels[0] = '/' + raw_labels[0].strip()

    for label in raw_labels:
        try:

            if '/' in label.strip()[0]:
                heads = label.replace('/', '').strip().split()

            else:
                for label_value in exclude_empty_values(label.split("' ")):
                    try:

                        v_name, *v_value = label_value.split("'")

                        for head in force_list(heads):

                            add_element(
                                headers,
                                '{}/value_label'.format(head.strip()),
                                {v_name.strip(): " ".join(force_list(v_value)).strip()},
                                digit=False)

                    except Exception as ex:
                        logger.error('Fail to parse label value {}'.format(ex), label_value=label_value)
                        continue

        except Exception as ex:
            logger.error('Fail to parse variable label - {}'.format(ex), label=label)


def parse_spss_header_labels(raw_labels, headers={}, **kwargs):
    try:
        raw_labels_splited = exclude_empty_values(raw_labels.split('\r\n'))

        if 'value' in raw_labels_splited[0].lower():
            parse_value_label(raw_labels_splited[1:], headers)

        else:
            parse_variable_label(raw_labels_splited[1:], headers)

    except Exception as ex:
        logger.error('Fail to parse leyend - {}'.format(ex))

    return headers


def parse_spss_headerfile(path, **kwargs):
    """
    Parse spss header file

    Arguments:
        path {str} -- path al fichero de cabecera.
        leyend_position -- posicion del la leyenda en el header.
    """
    headers_clean = {}
    try:
        with codecs.open(path, 'r', kwargs.get('encoding', 'latin-1')) as file_:
            raw_file = file_.read()
            raw_splited = exclude_empty_values(raw_file.split('.\r\n'))

            # suposse that by default spss leyend is in position 0.
            leyend = parse_spss_header_leyend(
                raw_leyend=raw_splited.pop(kwargs.get('leyend_position', 0)),
                leyend=headers_clean)

            if not leyend:
                raise Exception('Empty leyend')

            # only want VARIABLE(S) LABEL(S) & VALUE(S) LABEL(S)
            for label in [x for x in raw_splited if 'label' in x.lower()]:
                values = parse_spss_header_labels(
                    raw_labels=label,
                    headers=leyend)

    except Exception as ex:
        logger.error('Fail to parse spss headerfile - {}'.format(ex), header_file=path)
        headers_clean = {}

    return headers_clean


def parse_spss_datafile(path, **kwargs):
    """
    Parse spss data file

    Arguments:
        path {str} -- path al fichero de cabecera.
        **kwargs {[dict]} -- otros argumentos que puedan llegar
    """
    data_clean = []
    with codecs.open(path, 'r', kwargs.get('encoding', 'latin-1')) as file_:
        raw_file = file_.read()
        data_clean = raw_file.split('\r\n')
    return exclude_empty_values(data_clean)


def join_spss_header_data(header, data, question_dict={}, **kwargs):
    joined_results = []

    # lenght of data
    num_data = len(data)

    for i, data_raw in enumerate(data):
        try:
            if i % 50 == 0:
                logger.debug('Joining spss header with data {} / {}'.format(i, num_data))

            partial_results = {}
            for key, header_data in header.items():
                try:
                    columns_raw = header_data.get('columns')

                    if not columns_raw:
                        continue

                    columns = slice(*columns_raw)

                    response_raw = data_raw[columns].strip()
                    response = header_data.get('value_label', {}).get(response_raw) or header_data.get('value_label', {}).get('0' + response_raw) or response_raw

                    partial_results[key] = {
                        'question': question_dict.get(key),
                        'variable_label': header_data.get('variable_label'),
                        'response': response.strip()
                    }
                except Exception as ex:
                    logger.error("Fail to parse header key".format(ex), key=key)
                    continue

        except Exception as ex:
            logger.error("".format('Fail to parse data_raw - {}'.format(ex)))
            continue

        joined_results.append(exclude_empty_values(partial_results))
    return joined_results


def parse_spss(header_filepath, data_filepath, **kwargs):

    result = {}

    try:
        # parse header
        header = parse_spss_headerfile(header_filepath, **kwargs)

        # parse data
        data = parse_spss_datafile(data_filepath, **kwargs)

        # join header & data
        result = join_spss_header_data(header, data, **kwargs)

    except Exception as ex:
        logger.error('Fail to parse spss - {}'.format(ex), header=header_filepath, data=data_filepath)

    return result
