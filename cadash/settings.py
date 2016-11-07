# -*- coding: utf-8 -*-
"""Application configuration."""
import os


class Config(object):
    """configuration object."""

    SECRET_KEY = os.environ.get('FLASK_SECRET', 'secret-key')
    APP_DIR = os.path.abspath(os.path.dirname(__file__))  # This directory
    PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, os.pardir))

    DEBUG = True
    ASSETS_DEBUG = True  # do not bundle/minify static assets
    DEBUG_TB_ENABLED = True  # enable Debug toolbar
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    LOG_CONFIG = os.environ.get('LOG_CONFIG', 'logging.yaml')

    # disable tracking
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # app in-memory cache
    CACHE_TYPE = 'simple'  # Can be "memcached", "redis", etc.

    # ca_stats creds to pull info on all capture agents
    CA_STATS_JSON_URL = 'http://ca_stats_fake_url.com'
    CA_STATS_USER = 'ca_stats_fake_user'
    CA_STATS_PASSWD = 'ca_stats_fake_passwd'

    # epipearl creds (to talk to capture agents) mandatory
    EPIPEARL_USER = 'epipearl_fake_user'
    EPIPEARL_PASSWD = 'epipearl_fake_passwd'

    # ldap info is mandatory
    LDAP_HOST = 'fake_ldap_server.fake.com'
    LDAP_BASE_SEARCH = 'dc=fake,dc=com'
    LDAP_BIND_DN = 'dn=fake_super_user,dc=fake,dc=com'
    LDAP_BIND_PASSWD = 'passw0rd'


    def __init__(self, environment='prod', login_disabled=False):
        """create instance."""
        env = environment.lower()

        if env == 'dev':
            self.ENV = 'dev'

            # Put the db file in project root
            self.DB_NAME = 'dev.db'
            self.DB_PATH = os.path.join(Config.PROJECT_ROOT, self.DB_NAME)
            self.SQLALCHEMY_DATABASE_URI = 'sqlite:///{0}'.format(self.DB_PATH)

            # ca_stats creds is mandatory
            self.CA_STATS_JSON_URL = os.environ.get('CA_STATS_JSON_URL', 'http://ha.com')
            self.CA_STATS_USER = os.environ.get('CA_STATS_USER', 'user1')
            self.CA_STATS_PASSWD = os.environ.get('CA_STATS_PASSWD', 'pwd1')

            # epipearl creds (to talk to capture agents) mandatory
            self.EPIPEARL_USER = os.environ.get('EPIPEARL_USER', 'user2')
            self.EPIPEARL_PASSWD = os.environ.get('EPIPEARL_PASSWD', 'pwd2')

            # ldap info is mandatory
            self.LDAP_HOST = os.environ.get('LDAP_HOST', 'ho.com')
            self.LDAP_BASE_SEARCH = os.environ.get('LDAP_BASE_SEARCH', 'dc=ho,dc=com')
            self.LDAP_BIND_DN = os.environ.get('LDAP_BIND_DN', 'dn=user3,dc=ho,dc=com')
            self.LDAP_BIND_PASSWD = os.environ.get('LDAP_BIND_PASSWD', 'pwd3')

        elif env == 'test':
            self.ENV = 'test'
            self.TESTING = True
            self.SQLALCHEMY_DATABASE_URI = 'sqlite://'
            self.CACHE_TYPE = 'simple'  # Can be "memcached", "redis", etc.
            self.WTF_CSRF_ENABLED = False  # Allows form testing

            if login_disabled:
                # disabled login_required for unit tests
                self.LOGIN_DISABLED = True
                # see https://github.com/jarus/flask-testing/issues/21
                self.PRESERVE_CONTEXT_ON_EXCEPTION = False

        elif env == 'prod':
            self.ENV = 'prod'
            self.DEBUG = False
            self.ASSETS_DEBUG = False
            self.DEBUG_TB_ENABLED = False

            # production db can be in different mount!
            assert 'DB_NAME' in os.environ.keys(), 'missing env var "DB_NAME"'
            assert 'DB_DIR' in os.environ.keys(), 'missing env var "DB_DIR"'
            self.DB_NAME = os.environ['DB_NAME']
            self.DB_PATH = os.path.join(os.environ['DB_DIR'], self.DB_NAME)
            self.SQLALCHEMY_DATABASE_URI = 'sqlite:///{0}'.format(self.DB_PATH)

            # redis cache
            self.CACHE_TYPE = 'redis'
            self.CACHE_REDIS_HOST = 'localhost'
            self.CACHE_REDIS_PORT = 6379

            # ca_stats creds is mandatory
            assert 'CA_STATS_JSON_URL' in os.environ.keys(), 'missing env var "CA_STATS_JSON_URL"'
            assert 'CA_STATS_USER' in os.environ.keys(), 'missing env var "CA_STATS_USER"'
            assert 'CA_STATS_PASSWD' in os.environ.keys(), 'missing env var "CA_STATS_PASSWD"'
            self.CA_STATS_JSON_URL = os.environ['CA_STATS_JSON_URL']
            self.CA_STATS_USER = os.environ['CA_STATS_USER']
            self.CA_STATS_PASSWD = os.environ['CA_STATS_PASSWD']

            # epipearl creds (to talk to capture agents) mandatory
            assert 'EPIPEARL_USER' in os.environ.keys(), 'missing env var "EPIPEARL_USER"'
            assert 'EPIPEARL_PASSWD' in os.environ.keys(), 'missing env var "EPIPEARL_PASSWD"'
            self.EPIPEARL_USER = os.environ['EPIPEARL_USER']
            self.EPIPEARL_PASSWD = os.environ['EPIPEARL_PASSWD']

            # ldap info is mandatory
            assert 'LDAP_HOST' in os.environ.keys(), 'missing env var "LDAP_HOST"'
            assert 'LDAP_BASE_SEARCH' in os.environ.keys(), 'missing env var "LDAP_BASE_SEARCH"'
            assert 'LDAP_BIND_DN' in os.environ.keys(), 'missing env var "LDAP_BIND_DN"'
            assert 'LDAP_BIND_PASSWD' in os.environ.keys(), 'missing env var "LDAP_BIND_PASSWD"'
            self.LDAP_HOST = os.environ['LDAP_HOST']
            self.LDAP_BASE_SEARCH = os.environ['LDAP_BASE_SEARCH']
            self.LDAP_BIND_DN = os.environ['LDAP_BIND_DN']
            self.LDAP_BIND_PASSWD = os.environ['LDAP_BIND_PASSWD']

        else:
            raise ValueError('unknown environment: %s' % env)
