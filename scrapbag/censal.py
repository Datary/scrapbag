# -*- coding: utf-8 -*-
"""
Scrapbag censal file.
"""
import os
from .csvs import csv_tolist
from .strings import normalizer
from .collections import add_element, force_list, flatten

import structlog

logger = structlog.getLogger(__name__)

COMUNIDADES_DATA_PATH = os.path.join(
    "/".join(os.path.abspath(__file__).split('/')[:-1]),
    'data-aux/18codcom.csv')

PROVINCIAS_DATA_PATH = os.path.join(
    "/".join(os.path.abspath(__file__).split('/')[:-1]),
    'data-aux/18codprov.csv')

LOCALIDADES_DATA_PATH = os.path.join(
    "/".join(os.path.abspath(__file__).split('/')[:-1]),
    'data-aux/18codmun.csv')


class IneCensal():

    index_comunidades = {}
    index_comunidades_code = {}
    index_provincias = {}
    index_provincias_code = {}
    index_localidades = {}

    def __init__(self, **kwargs):

        # load INE comunidades data
        list_comunidades = self.load_data(path=COMUNIDADES_DATA_PATH, **kwargs)

        # load INE provincia data
        lista_provincias = self.load_data(path=PROVINCIAS_DATA_PATH, **kwargs)

        # load Ine file localidades data
        lista_localidad = self.load_data(path=LOCALIDADES_DATA_PATH, **kwargs)

        # generate the index
        self.index_comunidades, self.index_comunidades_code = self.make_index(list_comunidades)
        self.index_provincias, self.index_provincias_code = self.make_index(lista_provincias)
        self.index_localidades = self.make_index_localidades(lista_localidad)

    def load_data(self, path, **kwargs):

        return csv_tolist(path, delimiter=';')

    def make_index(self, lista):

        ine_censo_index = {}
        ine_censo_inverted = {}

        # first row is headers
        for censo_data in lista[1:]:
            try:

                # In ine file data, there are some rows with this pattern,
                # 'florida, La' and we want to change to 'La florida'
                for c_name in censo_data[1].split('/'):
                    c_clean_name = None

                    if ',' in c_name:
                        c_clean_name = " ".join(c_name.split(', ')[::-1])
                    else:
                        c_clean_name = c_name

                ine_censo_index[normalizer(c_clean_name)] = censo_data[0]

                if censo_data[0] in ine_censo_inverted:
                    ine_censo_inverted[censo_data[0]] = "/".join([ine_censo_inverted[censo_data[0]], normalizer(c_clean_name)])
                else:
                    ine_censo_inverted[censo_data[0]] = normalizer(c_clean_name)

            except Exception as ex:
                logger.error('Fail to make index with parsed row data {} - {}'.format(censo_data, ex))

        return ine_censo_index, ine_censo_inverted

    def make_index_localidades(self, lista):

        ine_censo_index = {}

        # first row is headers
        for censo_data in lista[1:]:
            try:

                # In ine file data, there are some rows with this pattern,
                # 'florida, La' and we want to change to 'La florida'

                for c_name in censo_data[4].split('/'):
                    c_clean_name = None

                    if ',' in c_name:
                        c_clean_name = " ".join(c_name.replace('/', '-').split(', ')[::-1])
                    else:
                        c_clean_name = c_name

                    key = "{}/{}/{}".format(
                        normalizer(c_clean_name),
                        self.index_provincias_code.get(censo_data[1]),
                        self.index_comunidades_code.get(censo_data[0]),
                        )

                    add_element(ine_censo_index, key, "".join(censo_data[1:3]))

            except Exception as ex:
                logger.error('Fail to make index with parsed row data {} - {}'.format(censo_data, ex))

        return ine_censo_index

    def get_codigo_censal(self, name, level=0, index={}, force_check=False, without_codigo_censal=set()):
        try:

            name = force_list(name)

            if not index:
                index = self.index_localidades

            # assert input name normalizer
            # name_level = normalizer(name[level].replace('/', '-'))
            for name_level in name[level].split('/'):

                name_level = normalizer(name_level)

                codigo_censal = index.get(name_level, None)

                # if not found in dict let search it by string name
                if not codigo_censal:
                    result_key = None
                    search_data = list(index.keys())

                    if "_".join(name[:level+1]) not in without_codigo_censal:

                        for name_word in name_level.split('-'):
                            logger.debug('*Searching {}'.format(name_word))

                            if len(name_word) == 1:
                                continue

                            if not search_data:
                                break

                            for search_name in iter(list(search_data)):
                                if name_word not in search_name:
                                    search_data.remove(search_name)

                            if len(search_data) == 1:

                                # same word lenght
                                if len(search_data[0].split('-')) == len(name_level.split('-')):
                                    result_key = search_data[0]
                                    logger.debug('*** Found codigo censal: {}'.format(result_key))

                                    if (len(flatten(index.get(result_key, {}))) > 1 or (force_check == True and len(name[level:]) > 1)):

                                        if len(name[level:]) == 1:
                                            raise Exception('Need more level info {}'.format(codigo_censal))

                                        codigo_censal = self.get_codigo_censal(name, level+1, index.get(result_key, {}), force_check, without_codigo_censal)

                                    else:
                                        codigo_censal = [x for x in flatten(index.get(result_key)).values()][0]

                                    break

                    if result_key is None:
                        without_codigo_censal.add("_".join(name[:level+1]))
                        logger.error('* -- Fail Searching codigo_censal {}'.format(name))

                # if found the code in this level, return it
                elif not isinstance(codigo_censal, dict):
                    return codigo_censal

                # if got more than 1 level in result hierarchy
                elif (len(flatten(codigo_censal)) > 1 or (force_check == True and len(name[level:]) > 1)):

                    if len(name[level:]) == 1:
                        raise Exception('Need more level info {}'.format(codigo_censal))

                    codigo_censal = self.get_codigo_censal(name, level+1, codigo_censal, force_check, without_codigo_censal)

                # if have a simple hierarchy with one level
                else:
                    codigo_censal = [x for x in flatten(codigo_censal).values()][0]

                # not needed alternative name iteration so break
                if codigo_censal:
                    break

        except Exception as ex:
            without_codigo_censal.add("_".join(name[:level+1]))
            codigo_censal = None
            logger.error('Fail to retrieve codigo censal - {}'.format(ex))

        return codigo_censal

    def get_codigo_provincia(self, name):
        return self.index_provincias.get(name)

    def get_provincia(self, codigo_provincia):
        return self.index_provincias_code.get(str(codigo_provincia))

    def get_codigo_comunidad(self, name):
        return self.index_comunidades.get(name)

    def get_comunidad(self, codigo_comunidad):
        return self.index_comunidades_code.get(str(codigo_comunidad))
