# -*- coding: utf-8 -*-
"""
Scrapbag collections file.
"""
import re
import collections
from functools import reduce
from scrapbag.strings import exclude_chars

import structlog

logger = structlog.getLogger(__name__)


def exclude_values(values, args):
    """
    Exclude data with specific value.
    =============   =============   =======================================
    Parameter       Type            Description
    =============   =============   =======================================
    values          list            values where exclude elements
    args            list or dict    elements to exclude
    =============   =============   =======================================
    Returns: vakues without excluded elements
    """

    if isinstance(args, dict):
        return {
            key: value
            for key, value in (
                (k, exclude_values(values, v)) for (k, v) in args.items())
            if value not in values
        }
    elif isinstance(args, list):
        return [
            item
            for item in [exclude_values(values, i) for i in args]
            if item not in values
        ]

    return args


def exclude_empty_values(args):
    """
    Exclude None, empty strings and empty lists using exclude_values.
    Empry touples positions not included
    =============   =============   =======================================
    Parameter       Type            Description
    =============   =============   =======================================
    args            list or dict    elements to exclude
    =============   =============   =======================================
    Returns: values without excluded values introduces and without defined
    empty values.
    """
    empty_values = ['', 'None', None, [], {}]
    return exclude_values(empty_values, args)


def check_fields(fields, args):
    """Check that every field given in fields is included in args.args.

    - fields (tuple): fieldes to be searched in args
    - args (dict): dictionary whose keys will be checked against fields
    """
    for field in fields:
        if field not in args:
            return False
    return True


def get_element(source, path, separator=r'[/.]'):
    """
    Given a dict and path '/' or '.' separated. Digs into de dict to retrieve
    the specified element.

    Args:
        source (dict): set of nested objects in which the data will be searched
        path (string): '/' or '.' string with attribute names
    """
    return _get_element_by_names(source, re.split(separator, path))


def _get_element_by_names(source, names):
    """
    Given a dict and path '/' or '.' separated. Digs into de dict to retrieve
    the specified element.

    Args:
        source (dict): set of nested objects in which the data will be searched
        path (list): list of attribute names
    """

    if source is None:
        return source

    else:
        if names:
            head, *rest = names
            if isinstance(source, dict) and head in source:
                return _get_element_by_names(source[head], rest)
            elif isinstance(source, list) and head.isdigit():
                return _get_element_by_names(source[int(head)], rest)
            elif not names[0]:
                pass
            else:
                source = None
        return source


def add_element(source, path, value, separator=r'[/.]', **kwargs):
    """
    Add element into a list or dict easily using a path.
    =============   =============   =======================================
    Parameter       Type            Description
    =============   =============   =======================================
    source          list or dict    element where add the value.
    path            string          path to add the value in element.
    value           ¿all?           value to add in source.
    separator       regex string    Regexp to divide the path.
    =============   =============   =======================================
    Returns: source with added value
    """

    return _add_element_by_names(
        source,
        exclude_empty_values(re.split(separator, path)),
        value,
        **kwargs)


def _add_element_by_names(src, names, value, override=False, digit=True):
    """
    Internal method recursive to Add element into a list or dict easily using
    a path.
    =============   =============   =======================================
    Parameter       Type            Description
    =============   =============   =======================================
    src             list or dict    element where add the value.
    names           list            list with names to navigate in src.
    value           ¿all?           value to add in src.
    override        boolean         Override the value in path src.
    =============   =============   =======================================
    Returns: src with added value
    """

    if src is None:
        return False

    else:

        if names and names[0]:
            head, *rest = names

            # list and digit head
            if isinstance(src, list):
                if force_list(digit)[0] and head.isdigit():
                    head = int(head)

                    # if src is a list and lenght <= head
                    if len(src) <= head:
                        src.extend([""] * (head + 1 - len(src)))

            # head not in src :(
            elif isinstance(src, dict):
                if head not in src:
                    src[head] = [""] * (int(rest[0]) + 1) if rest and force_list(digit)[0] and rest[0].isdigit() else {}

            # more heads in rest
            if rest:

                # Head find but isn't a dict or list to navigate for it.
                if not isinstance(src[head], (dict, list)):

                    # only could be str for dict or int for list
                    src[head] = [""] * (int(rest[0]) + 1) if force_list(digit)[0] and rest[0].isdigit() else {}

                    digit = digit if not digit or not isinstance(digit, list) else digit[1:]

                    if not force_list(digit)[0] and rest and str(rest[0]).isdigit() and isinstance(src[head], list) and override:
                        src[head] = {}

                    _add_element_by_names(src[head], rest, value, override=override, digit=digit)

                else:

                    digit = digit if not digit or not isinstance(digit, list) else digit[1:]

                    if not force_list(digit)[0] and rest and str(rest[0]).isdigit() and isinstance(src[head], list) and override:
                        src[head] = {}

                    _add_element_by_names(src[head], rest, value, override=override, digit=digit)

            # it's final head
            else:

                if not override:

                    if isinstance(src, list) and isinstance(head, int):

                        if src[head] == '':
                            src[head] = value
                        else:
                            src.append(value)

                    elif isinstance(src[head], list):
                        src[head].append(value)

                    elif isinstance(src[head], dict) and isinstance(value, dict):
                        src[head].update(value)

                    else:
                        src[head] = value

                else:
                    src[head] = value

        return src


def format_dict(dic, format_list, separator=',', default_value=str):
    """
    Format dict to string passing a list of keys as order
    Args:
        lista: List with elements to clean duplicates.
    """

    dic = collections.defaultdict(default_value, dic)

    str_format = separator.join(["{" + "{}".format(head) + "}" for head in format_list])

    return str_format.format(**dic)


def force_list(element):
    """
    Given an element or a list, concatenates every element and clean it to
    create a full text
    """
    if element is None:
        return []

    if isinstance(element, (collections.Iterator, list)):
        return element

    return [element]


def simplify_collection(element, force_list=False, empty_values=['', 'None', None, [], {}], **kwargs):

    # if None
    if element is None:
        return None

    if isinstance(element, dict):
        element = {
            key: value
            for key, value in (
                (k, simplify_collection(
                    element=v,
                    force_list=force_list,
                    empty_values=empty_values)) for (k, v) in element.items())
        }

    # if list or tuple or collection iterable
    elif isinstance(element, (collections.Iterator, list)):
        element = exclude_values(empty_values, element)

        # simplify each sub_element in element
        for i in range(0, len(element)):
            element[i] = simplify_collection(
                element=exclude_values(empty_values, element[i]),
                force_list=force_list,
                empty_values=empty_values)

        if not force_list and len(element) == 1:
            element = element[0]

    return exclude_values(empty_values, element)


def chunks(lista, size):
    """Yield successive n-sized chunks from l."""
    if not isinstance(lista, list):
        logger.error('Erron in chunks, arg introduced is not a list.', lista=lista)
        return lista

    for i in range(0, len(lista), size):
        yield lista[i:i + size]


def flatten(data, parent_key='', sep='_'):
    """
    Transform dictionary multilevel values to one level dict, concatenating
    the keys with sep between them.
    """
    items = []

    if isinstance(data, list):
        logger.debug('Flattening list {}'.format(data))
        list_keys = [str(i) for i in range(0, len(data))]
        items.extend(
            flatten(dict(zip(list_keys, data)), parent_key, sep=sep).items())

    elif isinstance(data, dict):
        logger.debug('Flattening dict {}'.format(data))

        for key, value in data.items():
            new_key = parent_key + sep + key if parent_key else key
            if isinstance(value, collections.MutableMapping):
                items.extend(flatten(value, new_key, sep=sep).items())
            else:
                if isinstance(value, list):
                    list_keys = [str(i) for i in range(0, len(value))]
                    items.extend(
                        flatten(
                            dict(zip(list_keys, value)), new_key, sep=sep).items())
                else:
                    items.append((new_key, value))
    else:
        logger.debug('Nothing to flatten with {}'.format(data))
        return data

    return collections.OrderedDict(items)


def merge_dicts(base_dict, merge_dict, **kwargs):
    result = {}

    if isinstance(base_dict, dict) and isinstance(merge_dict, dict):

        f_merge_dict = flatten(merge_dict, sep='/')

        for k in f_merge_dict.keys():
            add_element(base_dict, k, get_element(merge_dict, k), **kwargs)

        result = base_dict

    else:
        logger.error('Arguments dicts are not dicts', base_dict=base_dict, merge_dict=merge_dict)

    return result


def nested_dict_to_list(path, dic, exclusion=None):
    """
    Transform nested dict to list
    """
    result = []
    exclusion = ['__self'] if exclusion is None else exclusion

    for key, value in dic.items():

        if not any([exclude in key for exclude in exclusion]):
            if isinstance(value, dict):
                aux = path + key + "/"
                result.extend(nested_dict_to_list(aux, value))
            else:
                if path.endswith("/"):
                    path = path[:-1]

                result.append([path, key, value])

    return result


def find_value_in_object(attr, obj):
    """Return values for any key coincidence with attr in obj or any other
    nested dict.
    """

    # Carry on inspecting inside the list or tuple
    if isinstance(obj, (collections.Iterator, list)):
        for item in obj:
            yield from find_value_in_object(attr, item)

    # Final object (dict or entity) inspect inside
    elif isinstance(obj, collections.Mapping):

        # If result is found, inspect inside and return inner results
        if attr in obj:

            # If it is iterable, just return the inner elements (avoid nested
            # lists)
            if isinstance(obj[attr], (collections.Iterator, list)):
                for item in obj[attr]:
                    yield item

            # If not, return just the objects
            else:
                yield obj[attr]

        # Carry on inspecting inside the object
        for item in obj.values():
            if item:
                yield from find_value_in_object(attr, item)


def remove_list_duplicates(lista, unique=False):
    """
    Remove duplicated elements in a list.
    Args:
        lista: List with elements to clean duplicates.
    """
    result = []
    allready = []

    for elem in lista:
        if elem not in result:
            result.append(elem)
        else:
            allready.append(elem)

    if unique:
        for elem in allready:
            result = list(filter((elem).__ne__, result))

    return result


def dict2orderedlist(dic, order_list, default='', **kwargs):
    """
    Return a list with dict values ordered by a list of key passed in args.
    """
    result = []
    for key_order in order_list:
        value = get_element(dic, key_order, **kwargs)
        result.append(value if value is not None else default)
    return result


def get_dimension(data):
    """
    Get dimension of the data passed by argument independently if it's an
    arrays or dictionaries
    """
    result = [0, 0]

    if isinstance(data, list):
        result = get_dimension_array(data)

    elif isinstance(data, dict):
        result = get_dimension_dict(data)

    return result


def get_dimension_dict(dictionary):
    """
    Get dimension of an dict passed by arg

    Arguments:
        dictionary {[dict]} -- [dict passed to take dimension]

    Returns:
        [list] -- [dictionary dimension size]
    """
    result = [1, len(dictionary)]
    return result


def get_dimension_array(array):
    """
    Get dimension of an array getting the number of rows and the max num of
    columns.
    """
    if all(isinstance(el, list) for el in array):
        result = [len(array), len(max([x for x in array], key=len,))]

    # elif array and isinstance(array, list):
    else:
        result = [len(array), 1]

    return result


def get_ldict_keys(ldict, flatten_keys=False, **kwargs):
    """
    Get first level keys from a list of dicts
    """
    result = []
    for ddict in ldict:
        if isinstance(ddict, dict):

            if flatten_keys:
                ddict = flatten(ddict, **kwargs)

            result.extend(ddict.keys())
    return list(set(result))


def get_alldictkeys(ddict, parent=None):
    """
    Get all keys in a dict
    """
    parent = [] if parent is None else parent

    if not isinstance(ddict, dict):
        return [tuple(parent)]
    return reduce(
        list.__add__,
        [get_alldictkeys(v, parent + [k]) for k, v in ddict.items()],
        [])


def clean_dictkeys(ddict, exclusions=None):
    """
    Exclude chars in dict keys and return a clean dictionary.
    """
    exclusions = [] if exclusions is None else exclusions

    if not isinstance(ddict, dict):
        return {}

    for key in list(ddict.keys()):
        if [incl for incl in exclusions if incl in key]:
            data = ddict.pop(key)
            clean_key = exclude_chars(key, exclusions)

            if clean_key:
                if clean_key in ddict:
                    ddict[clean_key] = force_list(ddict[clean_key])
                    add_element(ddict, clean_key, data)
                else:
                    ddict[clean_key] = data

        # dict case
        if isinstance(ddict.get(key), dict):
            ddict[key] = clean_dictkeys(ddict[key], exclusions)

        # list case
        elif isinstance(ddict.get(key), list):
            for row in ddict[key]:
                if isinstance(row, dict):
                    row = clean_dictkeys(row, exclusions)

    return ddict
