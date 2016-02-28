# -*- coding: utf-8 -*-
"""Defines fixtures available to all tests."""

from mock import patch
import pytest
from webtest import TestApp

from cadash.app import create_app
from cadash.database import db as _db
from cadash.ldap import LdapClient
from cadash.settings import TestConfig
from cadash.settings import TestConfig_LoginDisabled

from .factories import UserFactory


@pytest.yield_fixture(scope='function')
def app():
    """An application for the tests."""
    with patch.object(LdapClient, 'is_authenticated', return_value=True):
        _app = create_app(TestConfig)
    ctx = _app.test_request_context()
    ctx.push()

    yield _app

    ctx.pop()


@pytest.yield_fixture(scope='function')
def app_login_disabled():
    """An application for the tests."""
    with patch.object(LdapClient, 'is_authenticated', return_value=True):
        _app_nologin = create_app(TestConfig_LoginDisabled)
    ctx = _app_nologin.test_request_context()
    ctx.push()

    yield _app_nologin

    ctx.pop()


@pytest.fixture(scope='function')
def testapp(app):
    """A Webtest app."""
    return TestApp(app)


@pytest.fixture(scope='function')
def testapp_login_disabled(app_login_disabled):
    """A Webtest app."""
    return TestApp(app_login_disabled)


@pytest.yield_fixture(scope='function')
def db(app):
    """A database for the tests."""
    _db.app = app
    with app.app_context():
        _db.create_all()

    yield _db

    # Explicitly close DB connection
    _db.session.close()
    _db.drop_all()


@pytest.fixture
def user(db):
    """A user for the tests."""
    user = UserFactory(password='myprecious')
    db.session.commit()
    return user
