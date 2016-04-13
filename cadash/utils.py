# -*- coding: utf-8 -*-
"""Helper utilities and decorators."""
import os
import logging
import logging.config
import platform
import re
import sys
import yaml

from flask import flash
from flask import redirect
from flask import request
from flask import url_for
from flask_login import current_user
from functools import wraps
import requests
from requests.auth import HTTPBasicAuth

from cadash import __version__



def flash_errors(form, category='warning'):
    """Flash all errors for a form."""
    for field, errors in form.errors.items():
        for error in errors:
            flash('{0} - {1}'.format(getattr(form, field).label.text, error), category)


# from http://victorlin.me/posts/2012/08/26/good-logging-practice-in-python
def setup_logging(
        app,
        default_level=logging.INFO):
    """
    set up logging config.

    :param: app: application obj; relevant app.config['LOG_CONFIG']
            which is the full path to the yaml file with configs for logs
    :param: default_level: log level for basic config, default=INFO
    """
    if os.path.exists(app.config['LOG_CONFIG']):
        with open(app.config['LOG_CONFIG'], 'rt') as f:
            config = yaml.load(f.read())
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)

def clean_name(name):
    """
    clean `name` from non_alpha.

    replaces non-alpha with underscores '_' and set the string to lower case
    """
    return re.sub('[^0-9a-zA-Z]+', '_', name.strip()).lower()


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


def is_authorized(user, groups):
    """returns True if `user` in any group of list `groups`."""
    for g in groups:
        if user.is_in_group(g):
            return True
    return False

def requires_roles(*roles):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not is_authorized(current_user, *roles):
                flash('You need to login, or do not have credentials to access this page', 'info')
                return redirect(url_for('public.home', next=request.url))
            return f(*args, **kwargs)
        return wrapped
    return wrapper

