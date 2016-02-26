# -*- coding: utf-8 -*-
"""Application configuration."""
import os


class Config(object):
    """Base configuration."""

    SECRET_KEY = os.environ.get('CADASH_SECRET', 'secret-key')  # TODO: Change me
    APP_DIR = os.path.abspath(os.path.dirname(__file__))  # This directory
    PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, os.pardir))
    BCRYPT_LOG_ROUNDS = 13
    ASSETS_DEBUG = False
    DEBUG_TB_ENABLED = False  # Disable Debug toolbar
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    CACHE_TYPE = 'simple'  # Can be "memcached", "redis", etc.
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProdConfig(Config):
    """Production configuration."""

    ENV = 'prod'
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/example'  # TODO: Change me
    DEBUG_TB_ENABLED = False  # Disable Debug toolbar

    # ca_stats creds is mandatory
    assert 'CA_STATS_JSON_URL' in os.environ.keys(), 'missing env var "CA_STATS_JSON_URL"'
    assert 'CA_STATS_USER' in os.environ.keys(), 'missing env var "CA_STATS_USER"'
    assert 'CA_STATS_PASSWD' in os.environ.keys(), 'missing env var "CA_STATS_PASSWD"'
    CA_STATS_JSON_URL = os.environ['CA_STATS_JSON_URL']
    CA_STATS_USER = os.environ['CA_STATS_USER']
    CA_STATS_PASSWD = os.environ['CA_STATS_PASSWD']

    # epipearl creds (to talk to capture agents) mandatory
    assert 'EPIPEARL_USER' in os.environ.keys(), 'missing env var "EPIPEARL_USER"'
    assert 'EPIPEARL_PASSWD' in os.environ.keys(), 'missing env var "EPIPEARL_PASSWD"'
    EPIPEARL_USER = os.environ['EPIPEARL_USER']
    EPIPEARL_PASSWD = os.environ['EPIPEARL_PASSWD']

    # ldap info is mandatory
    assert 'LDAP_HOST' in os.environ.keys(), 'missing env var "LDAP_HOST"'
    assert 'LDAP_BASE_SEARCH' in os.environ.keys(), 'missing env var "LDAP_BASE_SEARCH"'
    assert 'LDAP_BIND_DN' in os.environ.keys(), 'missing env var "LDAP_BIND_DN"'
    assert 'LDAP_BIND_PASSWD' in os.environ.keys(), 'missing env var "LDAP_BIND_PASSWD"'
    LDAP_HOST = os.environ['LDAP_HOST']
    LDAP_BASE_SEARCH = os.environ['LDAP_BASE_SEARCH']
    LDAP_BIND_DN = os.environ['LDAP_BIND_DN']
    LDAP_BIND_PASSWD = os.environ['LDAP_BIND_PASSWD']


class DevConfig(ProdConfig):
    """Development configuration."""

    ENV = 'dev'
    DEBUG = True
    DB_NAME = 'dev.db'
    # Put the db file in project root
    DB_PATH = os.path.join(Config.PROJECT_ROOT, DB_NAME)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///{0}'.format(DB_PATH)
    DEBUG_TB_ENABLED = True
    ASSETS_DEBUG = True  # Don't bundle/minify static assets
    CACHE_TYPE = 'simple'  # Can be "memcached", "redis", etc.



class TestConfig(Config):
    """Test configuration."""

    ENV = 'test'
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    BCRYPT_LOG_ROUNDS = 4  # For faster tests; needs at least 4 to avoid "ValueError: Invalid rounds"
    WTF_CSRF_ENABLED = False  # Allows form testing

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


class TestConfig_LoginDisabled(TestConfig):
    """Disabled login_required for unit tests."""
    LOGIN_DISABLED = True

    # see https://github.com/jarus/flask-testing/issues/21
    PRESERVE_CONTEXT_ON_EXCEPTION = False
