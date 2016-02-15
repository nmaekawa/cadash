# -*- coding: utf-8 -*-
"""Utils for redunlive module."""
import logging
import platform
import re
import sys

import requests
from requests.auth import HTTPBasicAuth

from cadash import __version__


def clean_name(name):
    """
    clean `name` from non_alpha.

    replaces non-alpha with underscores '_' and set the string to lower case
    """
    return re.sub('[^0-9a-zA-Z]+', '_', name).lower()


def pull_data(url, creds=None):
    """
    get text file from `url`.

    reads a text file from given url
    if basic auth needed, pass args creds['user'] and creds['pwd']
    """
    headers = {
            'User-Agent': default_useragent(),
            'Accept-Encoding': 'gzip, deflate',
            'Accept': 'text/html, text/*'
            }
    au = None
    if creds is not None:
        if 'user' in creds and 'pwd' in creds:
            au = HTTPBasicAuth(creds['user'], creds['pwd'])
            headers.update({'X-REQUESTED-AUTH': 'Basic'})

    try:
        response = requests.get(url, headers=headers, auth=au)
    except requests.HTTPError as e:
        logger = logging.getLogger(__name__)
        logger.warning('data from url(%s) is unavailable. Error: %s' % (url, e))
        return None
    else:
        return response.text


def default_useragent():
    """Return a string representing the default user agent."""
    _implementation = platform.python_implementation()

    if _implementation == 'CPython':
        _implementation_version = platform.python_version()
    elif _implementation == 'PyPy':
        _implementation_version = '%s.%s.%s' % (sys.pypy_version_info.major,
                                                sys.pypy_version_info.minor,
                                                sys.pypy_version_info.micro)
        if sys.pypy_version_info.releaselevel != 'final':
            _implementation_version = ''.join(
                    [_implementation_version, sys.pypy_version_info.releaselevel])
    elif _implementation == 'Jython':
        _implementation_version = platform.python_version()  # Complete Guess
    elif _implementation == 'IronPython':
        _implementation_version = platform.python_version()  # Complete Guess
    else:
        _implementation_version = 'Unknown'

    try:
        p_system = platform.system()
        p_release = platform.release()
    except IOError:
        p_system = 'Unknown'
        p_release = 'Unknown'

    return ' '.join([
        '%s/%s' % (__name__, __version__),
        '%s/%s' % (_implementation, _implementation_version),
        '%s/%s' % (p_system, p_release)])
