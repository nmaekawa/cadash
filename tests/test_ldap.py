# -*- coding: utf-8 -*-
"""Test forms."""
import os
import pytest

from cadash.app import create_app
from cadash.ldap import LdapClient
from cadash.settings import Config
from cadash.utils import fetch_ldap_user


# control skipping live tests according to command line option --runlive
livetest = pytest.mark.skipif(
        not pytest.config.getoption('--runlive'),
        reason=(
            'need --runlive option to run, plus env vars',
            'LDAP_HOST, LDAP_BASE_SEARCH, LDAP_BIND_DN, LDAP_BIND_PASSWD'))


class TestLdapConnection(object):

    @livetest
    def test_connection(self):
        CONFIG = Config(environment='dev')
        app = create_app(CONFIG, 'cadash')
        ldap_cli = LdapClient()
        ldap_cli.init_app(app)

        user = fetch_ldap_user(
                usr='usr',
                pwd='pwd',
                cli=ldap_cli)
        assert user == 'blah'
