# -*- coding: utf-8 -*-
"""Test configs."""
from mock import patch

from cadash.app import create_app
from cadash.settings import DevConfig
from cadash.settings import ProdConfig

@patch('cadash.ldap.LdapClient.is_authenticated', return_value=True)
def test_production_config(mock_ldap_client):
    """Production config."""
    app = create_app(ProdConfig)
    assert app.config['ENV'] == 'prod'
    assert app.config['DEBUG'] is False
    assert app.config['DEBUG_TB_ENABLED'] is False
    assert app.config['ASSETS_DEBUG'] is False


@patch('cadash.ldap.LdapClient.is_authenticated', return_value=True)
def test_dev_config(mock_ldap_client):
    """Development config."""
    app = create_app(DevConfig)
    assert app.config['ENV'] == 'dev'
    assert app.config['DEBUG'] is True
    assert app.config['ASSETS_DEBUG'] is True
