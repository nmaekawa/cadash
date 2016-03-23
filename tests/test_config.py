# -*- coding: utf-8 -*-
"""Test configs."""
from mock import patch
import pytest

from cadash.app import create_app
from cadash.settings import Config

#def test_production_config():
#    """Production config."""
#    app = create_app()
#    assert app.config['ENV'] == 'prod'
#    assert app.config['DEBUG'] is False
#    assert app.config['DEBUG_TB_ENABLED'] is False
#    assert app.config['ASSETS_DEBUG'] is False


def test_dev_config():
    """Development config."""
    app = create_app(Config(environment='dev'))
    assert app.config['ENV'] == 'dev'
    assert app.config['DEBUG'] is True
    assert app.config['ASSETS_DEBUG'] is True


def test_invalid_environment():
    """get ValueError when pass an invalid env."""
    with pytest.raises(ValueError) as ve:
        app = create_app(Config(environment='sTaGe'))
    assert str(ve.value) == 'unknown environment: stage'
