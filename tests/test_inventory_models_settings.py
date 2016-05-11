# -*- coding: utf-8 -*-
"""Tests for `models` in redunlive webapp."""
import datetime as dt
import pytest

@pytest.mark.usefixtures('db', 'simple_db')
class TestSettings(object):
    """test component basic settings restrictions."""

    def test_create_comp_and_settings_not_null(self, simple_db):
        """settings not null, but date null."""
        assert simple_db['ca'][0].settings == u'{}'
        assert simple_db['ca'][0].settings_last_update is None

        assert simple_db['vendor'].settings == u'{}'
        assert simple_db['vendor'].settings_last_update is None

        assert simple_db['room'][0].settings == u'{}'
        assert simple_db['room'][0].settings_last_update is None

        assert simple_db['cluster'][0].settings == u'{}'
        assert simple_db['cluster'][0].settings_last_update is None


    def test_update_ca_settings_null(self, simple_db):
        """settings should still not be null, but date should be updated."""
        t0 = dt.datetime.utcnow()

        simple_db['ca'][0].update(settings=u'{"config1":"value1"}')
        t1 = simple_db['ca'][0].settings_last_update
        assert t1 > t0
        assert simple_db['ca'][0].settings == u'{"config1":"value1"}'
        simple_db['ca'][0].update(settings=None)
        t2 = simple_db['ca'][0].settings_last_update
        assert simple_db['ca'][0].settings == u'{}'
        assert t2 > t1


    def test_update_cluster_settings_null(self, simple_db):
        """settings should still not be null, but date should be updated."""
        t0 = dt.datetime.utcnow()

        simple_db['cluster'][0].update(settings=u'{"config1":"value1"}')
        t1 = simple_db['cluster'][0].settings_last_update
        assert t1 > t0
        assert simple_db['cluster'][0].settings == u'{"config1":"value1"}'
        simple_db['cluster'][0].update(settings=None)
        t2 = simple_db['cluster'][0].settings_last_update
        assert simple_db['cluster'][0].settings == u'{}'
        assert t2 > t1


    def test_update_location_settings_null(self, simple_db):
        """settings should still not be null, but date should be updated."""
        t0 = dt.datetime.utcnow()

        simple_db['room'][0].update(settings=u'{"config1":"value1"}')
        t1 = simple_db['room'][0].settings_last_update
        assert t1 > t0
        assert simple_db['room'][0].settings == u'{"config1":"value1"}'
        simple_db['room'][0].update(settings=None)
        t2 = simple_db['room'][0].settings_last_update
        assert simple_db['room'][0].settings == u'{}'
        assert t2 > t1


    def test_update_vendor_settings_null(self, simple_db):
        """settings should still not be null, but date should be updated."""
        t0 = dt.datetime.utcnow()

        simple_db['vendor'].update(settings=u'{"config1":"value1"}')
        t1 = simple_db['vendor'].settings_last_update
        assert t1 > t0
        assert simple_db['vendor'].settings == u'{"config1":"value1"}'
        simple_db['vendor'].update(settings=None)
        t2 = simple_db['vendor'].settings_last_update
        assert simple_db['vendor'].settings == u'{}'
        assert t2 > t1
