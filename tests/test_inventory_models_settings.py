# -*- coding: utf-8 -*-
"""Tests for `models` in redunlive webapp."""
import datetime as dt
import pytest

from cadash.caconf.settings_factory import SettingsFactory
from cadash.inventory.errors import DuplicateCaPackageNameError
from cadash.inventory.errors import InvalidOperationError
from cadash.inventory.models import CaPackage


@pytest.mark.usefixtures('db', 'simple_db')
class TestSettings(object):
    """test component basic settings restrictions."""

    def test_create_comp_and_settings_not_null(self, simple_db):
        """settings not null, but date null."""
        assert simple_db['ca'][0].settings == \
                SettingsFactory.settings_for_ca(simple_db['vendor'].name_id)
        assert simple_db['ca'][0].settings_last_update \
                < simple_db['ca'][0].created_at

        assert simple_db['vendor'].settings == \
                SettingsFactory.settings_for_vendor(simple_db['vendor'].name_id)
        assert simple_db['vendor'].settings_last_update \
                < simple_db['vendor'].created_at

        assert simple_db['room'][0].settings == \
                SettingsFactory.settings_for_location()
        assert simple_db['room'][0].settings_last_update \
                < simple_db['room'][0].created_at

        s = SettingsFactory.settings_for_cluster()
        s['mhpearl']['url'] = simple_db['cluster'][0].admin_host
        assert simple_db['cluster'][0].settings == s
        assert simple_db['cluster'][0].settings_last_update \
                < simple_db['cluster'][0].created_at

    def test_update_ca_settings_null(self, simple_db):
        """settings should still not be null, but date should be updated."""
        t0 = dt.datetime.utcnow()

        simple_db['ca'][0].update(settings={"config1":"value1"})
        t1 = simple_db['ca'][0].settings_last_update
        assert t1 > t0
        assert simple_db['ca'][0].settings == {"config1":"value1"}
        simple_db['ca'][0].update(settings=None)
        t2 = simple_db['ca'][0].settings_last_update
        assert simple_db['ca'][0].settings == {}
        assert t2 > t1


    def test_update_cluster_settings_null(self, simple_db):
        """settings should still not be null, but date should be updated."""
        t0 = dt.datetime.utcnow()

        simple_db['cluster'][0].update(settings={"config1":"value1"})
        t1 = simple_db['cluster'][0].settings_last_update
        assert t1 > t0
        assert simple_db['cluster'][0].settings == {"config1":"value1"}
        simple_db['cluster'][0].update(settings=None)
        t2 = simple_db['cluster'][0].settings_last_update
        assert simple_db['cluster'][0].settings == {}
        assert t2 > t1


    def test_update_location_settings_null(self, simple_db):
        """settings should still not be null, but date should be updated."""
        t0 = dt.datetime.utcnow()

        simple_db['room'][0].update(settings={"config1":"value1"})
        t1 = simple_db['room'][0].settings_last_update
        assert t1 > t0
        assert simple_db['room'][0].settings == {"config1":"value1"}
        simple_db['room'][0].update(settings=None)
        t2 = simple_db['room'][0].settings_last_update
        assert simple_db['room'][0].settings == {}
        assert t2 > t1


    def test_update_vendor_settings_null(self, simple_db):
        """settings should still not be null, but date should be updated."""
        t0 = dt.datetime.utcnow()

        simple_db['vendor'].update(settings={"config1":"value1"})
        t1 = simple_db['vendor'].settings_last_update
        assert t1 > t0
        assert simple_db['vendor'].settings == {"config1":"value1"}
        simple_db['vendor'].update(settings=None)
        t2 = simple_db['vendor'].settings_last_update
        assert simple_db['vendor'].settings == {}
        assert t2 > t1


@pytest.mark.usefixture('db', 'simple_db')
class TestCaPackage(object):
    """test capackage model."""

    def test_pkg_create_ok(self, simple_db):
        """create plain package."""
        pkg = CaPackage(name='blof',
                settings={"key1": "value1"}, deploy=False)
        assert pkg.name == 'blof'
        assert pkg.created_at is not None
        assert pkg.last_deployed is None

    def test_pkg_create_and_deploy(self, simple_db):
        """create package and set deploy date to now."""
        pkg = CaPackage(name='blof',
                settings={"key1": "value1"}, deploy=True)
        assert pkg.name == 'blof'
        assert pkg.created_at is not None
        assert pkg.last_deployed is not None
        assert pkg.last_deployed > pkg.created_at

    def test_pkg_duplicated_name(self, simple_db):
        """create pkg with a name already in inventory."""
        pkg1 = CaPackage(name='blof',
                settings={"key1": "value1"}, deploy=False)

        with pytest.raises(DuplicateCaPackageNameError) as e:
            pkg2 = CaPackage(name='blof',
                    settings={"key1": "value1"}, deploy=False)
        assert 'duplicate package name(blof)' in e.value.message

    def test_pkg_update_disabled(self, simple_db):
        """error when trying to update package."""
        pkg = CaPackage(name='blof',
                settings={"key1": "value1"}, deploy=False)
        assert pkg.last_deployed is None

        with pytest.raises(InvalidOperationError) as e:
            pkg.update(settings={"key1": "valueBLO"})
        assert 'not allowed to update `capackage`' in e.value.message

        pkg.deploy_now()
        assert pkg.last_deployed is not None
        assert pkg.last_deployed > pkg.created_at

    def test_pkg_delete_disabled(self, simple_db):
        """error when trying to delete package."""
        pkg = CaPackage(name='blof',
                settings={"key1": "value1"}, deploy=False)

        with pytest.raises(InvalidOperationError) as e:
            pkg.delete()
        assert 'not allowed to delete `capackage`' in e.value.message
