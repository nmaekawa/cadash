# -*- coding: utf-8 -*-
"""Defines fixtures available to all tests."""

from mock import patch
import pytest
from webtest import TestApp

from cadash.app import create_app
from cadash.database import db as _db
from cadash.inventory.models import Role
from cadash.ldap import LdapClient
from cadash.settings import Config

from tests.factories import CaFactory
from tests.factories import LocationFactory
from tests.factories import MhClusterFactory
from tests.factories import VendorFactory


@pytest.yield_fixture(scope='function')
def app():
    """An application for the tests."""
    with patch.object(LdapClient, 'is_authenticated', return_value=True):
        _app = create_app(Config(environment='test', login_disabled=False))
    ctx = _app.test_request_context()
    ctx.push()

    yield _app

    ctx.pop()


@pytest.yield_fixture(scope='function')
def app_login_disabled():
    """An application for the tests."""
    with patch.object(LdapClient, 'is_authenticated', return_value=True):
        _app_nologin = create_app(Config(environment='test', login_disabled=True))
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


@pytest.fixture(scope='function')
def simple_db(db):
    """a set of ca, location, mh, and vendor for tests."""
    mini_db = {}

    # create vendor
    v = VendorFactory()
    mini_db['vendor'] = v
    db.session.commit() # need the vendor.id to create ca

    # create a bunch of capture agents
    mini_db['ca'] = []
    for i in range(5):
        mini_db['ca'].append(CaFactory(vendor_id=mini_db['vendor'].id))

    # create a bunch of rooms
    mini_db['room'] = []
    for i in range(5):
        mini_db['room'].append(LocationFactory())

    # create a bunch of clusters
    mini_db['cluster'] = []
    for i in range(3):
        mini_db['cluster'].append(MhClusterFactory())

    db.session.commit()

    role_p1 = Role.create(location=mini_db['room'][0],
            ca=mini_db['ca'][0],
            cluster=mini_db['cluster'][0],
            name='experimental')
    role_p2 = Role.create(location=mini_db['room'][0],
            ca=mini_db['ca'][1],
            cluster=mini_db['cluster'][0],
            name='experimental')
    role_p3 = Role.create(location=mini_db['room'][0],
            ca=mini_db['ca'][2],
            cluster=mini_db['cluster'][0],
            name='primary')

    db.session.commit()

    return mini_db
