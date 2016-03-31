# -*- coding: utf-8 -*-
"""Tests for `models` in redunlive webapp."""
import datetime as dt
import pytest

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
        v = Vendor.create(name='ultramax', model='plus')
        ca = Ca.create(name='fake-epiphan', vendor=v,
                address='fake-epiphan.blah.bloh.net')
        retrieved = Ca.get_by_id(ca.id)
        assert retrieved == ca

    def test_created_at_defaults_to_datetime(self):
        """test creation date."""
        v = Vendor.create(name='ultramax', model='plus')
        ca = Ca.create(name='fake-epiphan', vendor=v,
                address='fake-epiphan.blah.bloh.net')
        assert bool(ca.created_at)
        assert isinstance(ca.created_at, dt.datetime)

    def test_name_id(self):
        """test name_id is populated."""
        v = Vendor.create(name='ultramax', model='plus')
        ca = Ca.create(name='fake-epiphan[A]', vendor=v,
                address='fake-epiphan.blah.bloh.net')
        assert ca.name_id == 'fake_epiphan_a_'


@pytest.mark.usefixtures('db')
class TestLocationModel(object):
    """location tests."""

    def test_get_by_id(self):
        """get location by id."""
        loc = Location.create(name='room A')
        retrieved = Location.get_by_id(loc.id)
        assert retrieved == loc

    def test_created_at_defaults_to_datetime(self):
        """test creation date."""
        loc = Location.create(name='room A')
        assert bool(loc.created_at)
        assert isinstance(loc.created_at, dt.datetime)

    def test_name_id(self):
        """test name_id is populated."""
        loc = Location.create(name='room A')
        assert loc.name_id == 'room_a'


@pytest.mark.usefixtures('db')
class TestVendorModel(object):
    """tests for capture agent vendor."""

    def test_get_by_id(self):
        vendor = Vendor.create(name='epipoing', model='drumpf')
        retrieved = Vendor.get_by_id(vendor.id)
        assert retrieved == vendor

    def test_created_at_defaults_to_datetime(self):
        vendor = Vendor.create(name='epipoing', model='drumpf')
        assert bool(vendor.created_at)
        assert isinstance(vendor.created_at, dt.datetime)

    def test_name_id(self):
        vendor = Vendor.create(name='epiPoinG for', model='drumPf!')
        assert vendor.name_id == 'epipoing_for_drumpf_'


@pytest.mark.usefixtures('db')
class TestMhClusterModel(object):
    """test for mh cluster."""

    def test_get_by_id(self):
        cluster = MhCluster.create(name='zupT',
                admin_host='host.some.where', env='dev')
        retrieved = MhCluster.get_by_id(cluster.id)
        assert retrieved == cluster

    def test_created_at_defaults_to_datetime(self):
        cluster = MhCluster.create(name='zupT',
                admin_host='host.some.where', env='dev')
        assert bool(cluster.created_at)
        assert isinstance(cluster.created_at, dt.datetime)

    def test_name_id(self):
        cluster = MhCluster.create(name='zupT dee da',
                admin_host='host.some.where', env='dev')
        assert cluster.name_id == 'zupt_dee_da'

    def test_invalid_env_value(self):
        with pytest.raises(InvalidMhClusterEnvironmentError):
            cluster = MhCluster.create(name='zupT',
                    admin_host='host.some.where', env='test')

    def test_valid_env_value(self):
        cluster = MhCluster.create(name='zupT',
                admin_host='host.same.where', env='PRod')
        assert cluster.env == 'prod'


@pytest.mark.usefixtures('db', 'simple_db')
class TestRelationship(object):
    """test for relationship role."""

    def test_vendor_ca_relationship(self, simple_db):
        """test 1-many vendor-ca relationship."""
        ca_per_vendor = simple_db['vendor'].capture_agents
        assert bool(ca_per_vendor)
        assert len(ca_per_vendor) == 5

        ca = simple_db['ca'][0]
        assert bool(ca.vendor)
        assert ca.vendor.name_id == simple_db['vendor'].name_id


    def test_invalid_role(self, simple_db):
        """test if role name is valid."""
        with pytest.raises(InvalidCaRoleError):
            role = Role.create(location=simple_db['room'][0],
                    ca=simple_db['ca'][3],
                    cluster=simple_db['cluster'][0],
                    name='funky')


    def test_location_duplicate_primary(self, simple_db):
        """test constraint one primary per location."""
        with pytest.raises(AssociationError):
            role = Role.create(location=simple_db['room'][0],
                    ca=simple_db['ca'][3],
                    cluster=simple_db['cluster'][0],
                    name='primary')


    def test_location_duplicate_experimental(self, simple_db):
        """ test constraint many experimental per location."""
        role = Role.create(location=simple_db['room'][0],
                ca=simple_db['ca'][3],
                cluster=simple_db['cluster'][0],
                name='experimental')
        assert len(simple_db['room'][0].get_ca_by_role('experimental')) == 3


    def test_ca_already_has_role(self, simple_db):
        """test constraint one role per capture agent."""
        with pytest.raises(AssociationError):
            role = Role.create(location=simple_db['room'][1],
                    ca=simple_db['ca'][0],
                    cluster=simple_db['cluster'][1],
                    name='experimental')


    def test_update_role_disabled(self, simple_db):
        """test that updating role relationship is not allowed."""
        role = simple_db['ca'][0].role
        with pytest.raises(InvalidOperationError):
            role.update(name='primary')


@pytest.mark.usefixtures('db', 'simple_db')
class TestDelete(object):
    """test for relationship role."""

    def test_delete_role(self, simple_db):
        """delete role just undo associations."""
        assert len(simple_db['room'][0].get_ca_by_role('experimental')) == 2
        assert len(simple_db['room'][0].get_ca()) == 3
        role = simple_db['ca'][0].role
        ca_id = simple_db['ca'][0].id
        role.delete()
        assert Role.query.filter_by(ca_id=ca_id).first() is None
        assert simple_db['ca'][0].id == ca_id
        assert simple_db['ca'][0].role_name == None
        assert simple_db['ca'][1].role_name == 'experimental'
        assert simple_db['ca'][2].role_name == 'primary'
        assert simple_db['ca'][2].location.name == simple_db['room'][0].name
        assert len(simple_db['room'][0].get_ca_by_role('experimental')) == 1
        assert len(simple_db['cluster'][0].get_ca()) == 2


    def test_delete_room(self, simple_db):
        """delete room and undo associations."""
        assert len(simple_db['room'][0].get_ca_by_role('experimental')) == 2
        assert len(simple_db['room'][0].get_ca()) == 3
        room_id = simple_db['room'][0].id
        simple_db['room'][0].delete()
        assert not bool(Location.get_by_id(room_id))
        assert simple_db['ca'][0].role_name == None
        assert simple_db['ca'][1].role_name == None
        assert simple_db['ca'][2].role_name == None
        assert len(simple_db['cluster'][0].get_ca()) == 0


    def test_delete_cluster(self, simple_db):
        """delete cluster and undo associations."""
        assert len(simple_db['cluster'][0].get_ca_by_role('experimental')) == 2
        assert len(simple_db['cluster'][0].get_ca()) == 3
        cluster_id = simple_db['cluster'][0].id
        simple_db['cluster'][0].delete()
        assert not bool(MhCluster.get_by_id(cluster_id))
        assert simple_db['ca'][0].role_name == None
        assert simple_db['ca'][1].role_name == None
        assert simple_db['ca'][2].role_name == None
        assert len(simple_db['cluster'][0].get_ca()) == 0


    def test_delete_vendor(self, simple_db):
        """delete associated ca's and ca's associations."""
        with pytest.raises(InvalidOperationError):
            simple_db['vendor'].delete()

    def test_delete_ca(self, simple_db):
        ca_id = simple_db['ca'][0].id
        simple_db['ca'][0].delete()
        assert Ca.get_by_id(ca_id) is None

