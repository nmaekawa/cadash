# -*- coding: utf-8 -*-
"""Defines fixtures available to all tests."""

from mock import patch
import pytest
from webtest import TestApp

from cadash.app import create_app
from cadash.database import db as _db
from cadash.inventory.models import AkamaiStreamingConfig
from cadash.inventory.models import EpiphanChannel
from cadash.inventory.models import EpiphanRecorder
from cadash.inventory.models import MhpearlConfig
from cadash.inventory.models import Role
from cadash.inventory.models import RoleConfig
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
        mini_db['ca'][i].capture_card_id = '11111111111{}'.format(i)

    # create a bunch of rooms
    mini_db['room'] = []
    for i in range(5):
        mini_db['room'].append(LocationFactory())

    # create a bunch of clusters
    mini_db['cluster'] = []
    for i in range(3):
        mini_db['cluster'].append(MhClusterFactory())

    # create streaming config
    stream_cfg = AkamaiStreamingConfig.create(
            name='fake_prod', stream_id='stream_id123',
            stream_user='stream_user123', stream_password='stream_pwd123')
    mini_db['stream_config'] = stream_cfg

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

    # create channels, recorders, mhcfg for ca[0]
    ca = mini_db['ca'][0]
    epi_config = RoleConfig.create(role=ca.role)
    stream_cfg = mini_db['stream_config']
    chan1 = EpiphanChannel.create(name='fake_channel',
            epiphan_config=epi_config, stream_cfg=mini_db['stream_config'])
    chan2 = EpiphanChannel.create(name='another_fake_channel',
            epiphan_config=epi_config)
    rec1 = EpiphanRecorder.create(name='recorder_fake', epiphan_config=epi_config)
    rec2 = EpiphanRecorder.create(name='recorder_fake_2', epiphan_config=epi_config)
    mh_cfg = MhpearlConfig.create(epiphan_config=epi_config)

    return mini_db
