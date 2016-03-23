# -*- coding: utf-8 -*-
"""Tests for `models` in redunlive webapp."""
import datetime as dt
import httpretty
import pytest
from epipearl import Epipearl

from cadash.inventory.models import Ca
from cadash.inventory.models import Location
from cadash.inventory.models import Vendor
from cadash.inventory.models import MhCluster
from cadash.inventory.errors import InvalidMhClusterEnvironmentError

@pytest.mark.usefixtures('db')
class TestCaptureAgentModel(object):
    """capture agent tests."""

    def test_get_by_id(self):
        """get ca by id."""
        ca = Ca(name='fake-epiphan', address='fake-epiphan.blah.bloh.net')
        ca.save()
        retrieved = Ca.get_by_id(ca.id)
        assert retrieved == ca


    def test_created_at_defaults_to_datetime(self):
        """test creation date."""
        ca = Ca(name='fake-epiphan', address='fake-epiphan.blah.bloh.net')
        ca.save()
        assert bool(ca.created_at)
        assert isinstance(ca.created_at, dt.datetime)

    def test_name_id(self):
        """test name_id is populated."""
        ca = Ca(name='fake-epiphan[A]', address='fake-epiphan.blah.bloh.net')
        ca.save()
        assert ca.name_id == 'fake_epiphan_a_'


@pytest.mark.usefixtures('db')
class TestLocationModel(object):
    """location tests."""

    def test_get_by_id(self):
        """get location by id."""
        loc = Location(name='room A')
        loc.save()
        retrieved = Location.get_by_id(loc.id)
        assert retrieved == loc


    def test_created_at_defaults_to_datetime(self):
        """test creation date."""
        loc = Location(name='room A')
        loc.save()
        assert bool(loc.created_at)
        assert isinstance(loc.created_at, dt.datetime)

    def test_name_id(self):
        """test name_id is populated."""
        loc = Location(name='room A')
        loc.save()
        assert loc.name_id == 'room_a'

@pytest.mark.usefixtures('db')
class TestVendorModel(object):
    """tests for capture agent vendor."""

    def test_get_by_id(self):
        vendor = Vendor(name='epipoing', model='drumpf')
        vendor.save()
        retrieved = Vendor.get_by_id(vendor.id)
        assert retrieved == vendor


    def test_created_at_defaults_to_datetime(self):
        vendor = Vendor(name='epipoing', model='drumpf')
        vendor.save()
        assert bool(vendor.created_at)
        assert isinstance(vendor.created_at, dt.datetime)


    def test_name_id(self):
        vendor = Vendor(name='epiPoinG for', model='drumPf!')
        vendor.save()
        assert vendor.name_id == 'epipoing_for_drumpf_'


@pytest.mark.usefixtures('db')
class TestMhClusterModel(object):
    """test for mh cluster."""

    def test_get_by_id(self):
        cluster = MhCluster(name='zupT', admin_host='host.some.where', env='dev')
        cluster.save()
        retrieved = MhCluster.get_by_id(cluster.id)
        assert retrieved == cluster

    def test_created_at_defaults_to_datetime(self):
        cluster = MhCluster(name='zupT', admin_host='host.some.where', env='dev')
        cluster.save()
        assert bool(cluster.created_at)
        assert isinstance(cluster.created_at, dt.datetime)

    def test_name_id(self):
        cluster = MhCluster(name='zupT dee da', admin_host='host.some.where', env='dev')
        cluster.save()
        assert cluster.name_id == 'zupt_dee_da'

    def test_invalid_env_value(self):
        with pytest.raises(InvalidMhClusterEnvironmentError):
            cluster = MhCluster(name='zupT', admin_host='host.some.where', env='test')

    def test_valid_env_value(self):
        cluster = MhCluster(name='zupT', admin_host='host.same.where', env='PRod')
        cluster.save()
        assert cluster.env == 'prod'
