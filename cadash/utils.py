# -*- coding: utf-8 -*-
"""Helper utilities and decorators."""
import os
import logging
import logging.config
import yaml

from flask import flash


def flash_errors(form, category='warning'):
    """Flash all errors for a form."""
    for field, errors in form.errors.items():
        for error in errors:
            flash('{0} - {1}'.format(getattr(form, field).label.text, error), category)


# from http://victorlin.me/posts/2012/08/26/good-logging-practice-in-python
def setup_logging(
        config_file_path='logging.yaml',
        env_key='LOG_CONFIG',
        default_level=logging.ERROR):
    """
    set up logging config

    :param: config_file_path: yaml logging config; default=logging.yaml
    :param: env_key: env var with yaml logging config, takes precedence
            over `config_file_path`; default=LOG_CONFIG
    :param: default_level: log level for basic config, default=ERROR
    """
    path = config_file_path
    value = os.getenv(env_key, None)

    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = yaml.load(f.read())
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)
