# -*- coding: utf-8 -*-
"""
Scrapbag files file.
"""
import re
import os
import time
import zipfile
import requests

import structlog

from .collections import force_list

logger = structlog.getLogger(__name__)


def open_filezip(file_path, find_str):
    """
    Open the wrapped file.
    Read directly from the zip without extracting its content.
    """
    if zipfile.is_zipfile(file_path):
        zipf = zipfile.ZipFile(file_path)
        interesting_files = [f for f in zipf.infolist() if find_str in f]

        for inside_file in interesting_files:
            yield zipf.open(inside_file)


def extract_filezip(path_to_file, dest_path, target_zipfiles=None):
    """
    Extract file zip to destiny path folder targeting only some kind of files.
    """

    target_zipfiles = ['.*'] if target_zipfiles is None else target_zipfiles

    files = []
    _, ext = os.path.splitext(path_to_file)

    if ext == '.zip':
        file = open(path_to_file, 'rb')
        with zipfile.ZipFile(file) as zip_file:
            regexp = '|'.join(target_zipfiles) if target_zipfiles else '.*'
            search_regex = re.compile(regexp)

            lista = [m.group() for x in zip_file.namelist()
                     for m in [search_regex.search(x)] if m]

            for zp_file in lista:
                try:
                    zip_file.extract(zp_file, dest_path)
                    files.append(os.path.join(dest_path, zp_file))
                except Exception as ex:
                    msg = 'Fail to extract {} in {} to {} - {}'.format(
                        zp_file, path_to_file, dest_path, ex)
                    logger.error(msg)
        file.close()
    else:
        logger.warning('Not zipfile passed in args')
    return files


def download_file(url, destination, **kwargs):
    """
    Download file  process:
        - Open the url
        - Check if it has been downloaded and it hanged.
        - Download it to  the destination folder.

    Args:
        :urls: url to take the file.
        :destionation: place to store the downloaded file.
    """
    web_file = open_remote_url(url, **kwargs)
    file_size = 0

    if not web_file:
        logger.error(
            "Remote file not found. Attempted URLs: {}".format(url))
        return

    modified = is_remote_file_modified(web_file, destination)
    if modified:
        logger.info("Downloading: " + web_file.url)
        file_size = copy_remote_file(web_file, destination)
    else:
        logger.info("File up-to-date: " + destination)

    web_file.close()
    return file_size


def open_remote_url(urls, **kwargs):
    """Open the url and check that it stores a file.
    Args:
        :urls: Endpoint to take the file
    """
    if isinstance(urls, str):
        urls = [urls]
    for url in urls:
        try:
            web_file = requests.get(url, stream=True, **kwargs)
            if 'html' in web_file.headers['content-type']:
                raise ValueError("HTML source file retrieved.")
            return web_file
        except Exception as ex:
            logger.error('Fail to open remote url - {}'.format(ex))
            continue


def is_remote_file_modified(web_file, destination):
    """
    Check if online file has been modified.
    Args:
        :web_file: online file to check.
        :destination: path of the offline file to compare.
    """
    try:
        # check datetime of last modified in file.
        last_mod = web_file.headers.get('last-modified')
        if last_mod:
            web_file_time = time.strptime(
                web_file.headers.get(
                    'last-modified'), '%a, %d %b %Y %H:%M:%S %Z')
        else:
            web_file_time = time.gmtime()

        web_file_size = int(web_file.headers.get('content-length', -1))
        if os.path.exists(destination):
            file_time = time.gmtime(os.path.getmtime(destination))
            file_size = os.path.getsize(destination)
            if file_time >= web_file_time and file_size == web_file_size:
                return False

    except Exception as ex:
        msg = ('Fail checking if remote file is modified default returns TRUE'
               ' - {}'.format(ex))
        logger.debug(msg)

    return True


def copy_remote_file(web_file, destination):
    """
    Check if exist the destination path, and copy the online resource
    file to local.

    Args:
        :web_file: reference to online file resource to take.
        :destination: path to store the file.
    """
    size = 0
    dir_name = os.path.dirname(destination)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

    with open(destination, 'wb') as file_:
        chunk_size = 8 * 1024
        for chunk in web_file.iter_content(chunk_size=chunk_size):
            if chunk:
                file_.write(chunk)
                size += len(chunk)
    return size


def remove_file(paths):
    """
    Remove file from paths introduced.
    """

    for path in force_list(paths):
        if os.path.exists(path):
            os.remove(path)
