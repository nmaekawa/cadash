# -*- coding: utf-8 -*-
"""ldap module, for dce auth via ldap server."""
from ldap3 import ALL_ATTRIBUTES
from ldap3 import Connection
from ldap3 import Server
import logging

class LdapClient(object):
    """simple ldap client for dce ldap server.

    assumes that anonymous connection is _never_ done!
    assumes that init_app() is called before any search or other call to ldap server.
    """

    def __init__(self, server=None, bind_dn=None, bind_password=None):
        """create instance."""
        self._server = server
        self._usr = bind_dn
        self._pwd = bind_password


    def init_app(self, app):
        """init ldap client instance, with configs from app."""
        self._server = Server(app.config['LDAP_HOST'], use_ssl=True)
        self._base_search = app.config['LDAP_BASE_SEARCH']
        self._usr = app.config['LDAP_BIND_DN']
        self._pwd = app.config['LDAP_BIND_PASSWD']
        # requiring ldap connection at this early stage of the app init
        # prevents use of manage.py!
        #if not self.is_authenticated(self._usr, self._pwd):
        #    raise ValueError('ldap user:password combination failed to authenticate')


    def is_authenticated(self, username, password):
        """authenticates user with ldap server."""
        conn = Connection(self._server, username, password)
        conn.open()
        conn.start_tls()
        result = conn.bind()
        conn.unbind()
        return result


    def fetch_groups(self, username):
        """fetch all ldap groups `username` belongs to."""
        result = []
        conn = Connection(self._server, self._usr, self._pwd)
        conn.open()
        conn.start_tls()
        # TODO: catch some exceptions
        if conn.bind():
            conn.search(
                    self._base_search,
                    '(&(objectclass=posixGroup)(memberUid=%s))' % username,
                    attributes=ALL_ATTRIBUTES)
            for e in conn.entries:
                result.append(e['cn'])
        else:
            logger = logging.get_logger(__name__)
            logger.error('bind usr(%s):pwd unknown' % self._usr)
        return result
