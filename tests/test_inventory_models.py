# -*- coding: utf-8 -*-
"""Tests for `models` in redunlive webapp."""
import datetime as dt
import httpretty
import pytest
from epipearl import Epipearl

from cadash.inventory.models import Ca
from cadash.inventory.models import Location
from cadash.inventory.models import MhCluster
from cadash.inventory.models import Role
from cadash.inventory.models import Vendor
from cadash.inventory.errors import AssociationError
from cadash.inventory.errors import InvalidCaRoleError
from cadash.inventory.errors import InvalidMhClusterEnvironmentError
from cadash.inventory.errors import InvalidOperationError

from tests.factories import CaFactory
from tests.factories import LocationFactory
from tests.factories import MhClusterFactory
from tests.factories import VendorFactory

@pytest.mark.usefixtures('db')
class TestCaptureAgentModel(object):
    """capture agent tests."""

    def test_get_by_id(self):
        """get ca by id."""
        v = Vendor(name='ultramax', model='plus')
        v.save()
        ca = Ca(name='fake-epiphan', vendor_id=v.id,
                address='fake-epiphan.blah.bloh.net')
        ca.save()
        retrieved = Ca.get_by_id(ca.id)
        assert retrieved == ca


    def test_created_at_defaults_to_datetime(self):
        """test creation date."""
        v = Vendor(name='ultramax', model='plus')
        v.save()
        ca = Ca(name='fake-epiphan', vendor_id=v.id,
                address='fake-epiphan.blah.bloh.net')
        ca.save()
        assert bool(ca.created_at)
        assert isinstance(ca.created_at, dt.datetime)

    def test_name_id(self):
        """test name_id is populated."""
        v = Vendor(name='ultramax', model='plus')
        v.save()
        ca = Ca(name='fake-epiphan[A]', vendor_id=v.id,
                address='fake-epiphan.blah.bloh.net')
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
        cluster = MhCluster(name='zupT dee da',
                admin_host='host.some.where', env='dev')
        cluster.save()
        assert cluster.name_id == 'zupt_dee_da'

    def test_invalid_env_value(self):
        with pytest.raises(InvalidMhClusterEnvironmentError):
            cluster = MhCluster(name='zupT',
                    admin_host='host.some.where', env='test')

    def test_valid_env_value(self):
        cluster = MhCluster(name='zupT', admin_host='host.same.where', env='PRod')
        cluster.save()
        assert cluster.env == 'prod'


@pytest.mark.usefixtures('db', 'simple_db')
class TestRoleRelationshipModel(object):
    """test for relationship role."""

    def test_vendor_ca_relationship(self, simple_db):
        """test 1-many vendor-ca relationship."""
        ca_per_vendor = simple_db['vendor'].capture_agents
        assert bool(ca_per_vendor)
        assert len(ca_per_vendor) == 5

        ca = simple_db['ca'][0]
        assert bool(ca.vendor)
        assert ca.vendor.name_id == 'vendor0_model0'


    def test_invalid_role(self, simple_db):
        """test if role name is valid."""
        r1 = simple_db['room'][0]
        c1 = simple_db['ca'][0]
        m1 = simple_db['cluster'][0]

        with pytest.raises(InvalidCaRoleError):
            role_p1 = Role(location_id=r1.id, ca_id=c1.id,
                    cluster_id=m1.id, name='funky')


    def test_location_duplicate_primary(self, simple_db):
        """test constraint one primary per location."""
        r1 = simple_db['room'][0]
        c1 = simple_db['ca'][0]
        c2 = simple_db['ca'][1]
        m1 = simple_db['cluster'][0]
        role_p1 = Role(location_id=r1.id, ca_id=c1.id,
                cluster_id=m1.id, name='primary')
        role_p1.save()

        with pytest.raises(AssociationError):
            role_p2 = Role(location_id=r1.id, ca_id=c2.id,
                    cluster_id=m1.id, name='primary')


    def test_location_duplicate_experimental(self, simple_db):
        """ test constraint many experimental per location."""
        r1 = simple_db['room'][0]
        c1 = simple_db['ca'][0]
        c2 = simple_db['ca'][1]
        m1 = simple_db['cluster'][0]
        role_p1 = Role(location_id=r1.id, ca_id=c1.id,
                cluster_id=m1.id, name='experimental')
        role_p1.save()
        role_p2 = Role(location_id=r1.id, ca_id=c2.id,
                cluster_id=m1.id, name='experimental')
        role_p2.save()
        assert len(r1.get_ca_by_role('experimental')) == 2


    def test_ca_already_has_role(self, simple_db):
        """test constraint one role per capture agent."""
        r1 = simple_db['room'][0]
        c1 = simple_db['ca'][0]
        m1 = simple_db['cluster'][0]
        role_p1 = Role(location_id=r1.id, ca_id=c1.id,
                cluster_id=m1.id, name='experimental')
        role_p1.save()

        with pytest.raises(AssociationError):
            role_p2 = Role(location_id=r1.id, ca_id=c1.id,
                    cluster_id=m1.id, name='experimental')


    def test_update_role_disabled(self, simple_db):
        """test that updating role relationship is not allowed."""
        r1 = simple_db['room'][0]
        c1 = simple_db['ca'][0]
        m1 = simple_db['cluster'][0]
        role_p1 = Role(location_id=r1.id, ca_id=c1.id,
                cluster_id=m1.id, name='experimental')
        role_p1.save()

        with pytest.raises(InvalidOperationError):
            role_p1.update(name='primary')







