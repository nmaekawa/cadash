# -*- coding: utf-8 -*-
"""Tests for `models` in redunlive webapp."""
import datetime as dt
import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.exc import SQLAlchemyError

from cadash import utils
from cadash.inventory.models import Ca
from cadash.inventory.models import Location
from cadash.inventory.models import MhCluster
from cadash.inventory.models import Role
from cadash.inventory.models import Vendor
from cadash.inventory.errors import AssociationError
from cadash.inventory.errors import DuplicateCaptureAgentNameError
from cadash.inventory.errors import DuplicateCaptureAgentAddressError
from cadash.inventory.errors import DuplicateCaptureAgentSerialNumberError
from cadash.inventory.errors import DuplicateLocationNameError
from cadash.inventory.errors import DuplicateMhClusterAdminHostError
from cadash.inventory.errors import DuplicateMhClusterNameError
from cadash.inventory.errors import DuplicateVendorNameModelError
from cadash.inventory.errors import InvalidCaRoleError
from cadash.inventory.errors import InvalidEmptyValueError
from cadash.inventory.errors import InvalidMhClusterEnvironmentError
from cadash.inventory.errors import InvalidOperationError
from cadash.inventory.errors import MissingVendorError

from tests.factories import CaFactory
from tests.factories import LocationFactory
from tests.factories import MhClusterFactory
from tests.factories import VendorFactory

@pytest.mark.usefixtures('db', 'simple_db')
class TestCaptureAgentModel(object):
    """capture agent tests."""

    def test_get_by_id(self, simple_db):
        """get ca by id."""
        ca = Ca.create(name='fake-epiphan',
                vendor_id=simple_db['vendor'].id,
                address='fake-epiphan.blah.bloh.net')
        retrieved = Ca.get_by_id(ca.id)
        assert retrieved == ca

    def test_created_at_defaults_to_datetime(self, simple_db):
        """test creation date."""
        ca = Ca.create(name='fake-epiphan',
                vendor_id=simple_db['vendor'].id,
                address='fake-epiphan.blah.bloh.net')
        assert bool(ca.created_at)
        assert isinstance(ca.created_at, dt.datetime)

    def test_name_id(self, simple_db):
        """test name_id is populated."""
        ca = Ca.create(name='fake-epiphan[A]',
                vendor_id=simple_db['vendor'].id,
                address='fake-epiphan.blah.bloh.net')
        assert ca.name_id == 'fake_epiphan_a_'

    def test_should_fail_when_create_ca_missing_vendor(self, simple_db):
        """vendor is mandatory for every capture agent."""
        with pytest.raises(MissingVendorError):
            ca = Ca.create(name='fake-epiphan',
                    vendor_id=999999,
                    address='fake-epiphan.blah.bloh.net')

    def test_should_fail_when_create_ca_duplicate_name(self, simple_db):
        """ca name is unique."""
        with pytest.raises(DuplicateCaptureAgentNameError):
            ca = Ca.create(name=simple_db['ca'][0].name,
                    vendor_id=simple_db['vendor'].id,
                    address='fake-epiphan.blah.bloh.net')

    def test_should_fail_when_create_ca_duplicate_address(self, simple_db):
        """ca address is unique."""
        with pytest.raises(DuplicateCaptureAgentAddressError):
            ca = Ca.create(name='fake-epiphan',
                    vendor_id=simple_db['vendor'].id,
                    address=simple_db['ca'][0].address)

    def test_should_fail_when_create_ca_duplicate_serial_number(self, simple_db):
        """ca serial_number is unique."""
        with pytest.raises(DuplicateCaptureAgentSerialNumberError):
            ca = Ca.create(name='fake-epiphan',
                    vendor_id=simple_db['vendor'].id,
                    address='fake-epiphan.blah.bloh.net',
                    serial_number=simple_db['ca'][0].serial_number)

    def test_update_ca_name(self, simple_db):
        """test update ca - happy path."""
        ca = Ca.get_by_id(simple_db['ca'][0].id)
        ca.update(name='new-name')
        assert ca.name == 'new-name'

        ca.update(name='blah', address='blah.some.domain', serial_number='xxx')
        assert ca.name == 'blah'
        assert ca.address == 'blah.some.domain'
        assert ca.serial_number == 'xxx'

    def test_should_fail_when_update_empty_ca_address(self, simple_db):
        """ca address is mandatory."""
        ca = Ca.get_by_id(simple_db['ca'][2].id)
        ca.update(serial_number='')
        assert ca.serial_number == ''

        with pytest.raises(InvalidEmptyValueError) as e:
            ca.update(address='')
        assert 'not allowed empty value for `address`' in str(e.value)

    def test_should_fail_when_update_not_updateable_ca_field(self, simple_db):
        """vendor_id is not allowed to be updated."""
        ca = Ca.get_by_id(simple_db['ca'][1].id)
        with pytest.raises(InvalidOperationError) as e:
            ca.update(vendor_id=simple_db['vendor'].id)
        assert 'not allowed to update ca fields: vendor_id' in str(e.value)



@pytest.mark.usefixtures('db', 'simple_db')
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

    def test_should_fail_when_create_location_duplicate_name(self, simple_db):
        """location name is unique."""
        with pytest.raises(DuplicateLocationNameError):
            loc = Location.create(name=simple_db['room'][0].name)

    def test_update(self, simple_db):
        """update happy path."""
        l = Location.get_by_id(simple_db['room'][0].id)
        l.update(name='new_name_for_room')
        l2 = Location.get_by_id(simple_db['room'][0].id)
        assert l2.name == 'new_name_for_room'

    def test_should_fail_when_update_location_duplicate_name(self, simple_db):
        """name is unique."""
        l = Location.get_by_id(simple_db['room'][0].id)
        with pytest.raises(DuplicateLocationNameError):
            l.update(name=simple_db['room'][1].name)

    def test_should_fail_when_update_not_updateable_field(self, simple_db):
        """capture_agents is not updateable."""
        l = Location.get_by_id(simple_db['room'][0].id)
        with pytest.raises(InvalidOperationError):
            l.update(capture_agents=[simple_db['ca'][3]])


@pytest.mark.usefixtures('db', 'simple_db')
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

    def test_should_fail_when_create_vendor_duplicate_name(self, simple_db):
        """vendor name_model is unique."""
        with pytest.raises(DuplicateVendorNameModelError):
            vendor = Vendor.create(name=simple_db['vendor'].name,
                    model=simple_db['vendor'].model)

    def test_update_vendor(self, simple_db):
        """test update happy path."""
        vendor = Vendor.get_by_id(simple_db['vendor'].id)
        vendor.update(name='fake')
        assert vendor.name_id == 'fake_%s' % utils.clean_name(vendor.model)

    def test_should_fail_when_update_duplicate_name_id(self, simple_db):
        """name_id unique."""
        vendor = Vendor.create(name=simple_db['vendor'].name, model='bloft')
        with pytest.raises(DuplicateVendorNameModelError):
            vendor.update(model=simple_db['vendor'].model)

    def test_should_fail_when_update_not_updateable_fields(self, simple_db):
        """name_id not updateable in vendor."""
        vendor = Vendor.get_by_id(simple_db['vendor'].id)
        with pytest.raises(InvalidOperationError) as e:
            vendor.update(name_id='fake-vendor')
        assert 'not allowed to update vendor fields: name_id' in str(e.value)



@pytest.mark.usefixtures('db', 'simple_db')
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

    def test_update_location(self, simple_db):
        """update happy path."""
        c = MhCluster.get_by_id(simple_db['cluster'][1].id)
        c.update(env='PrOd')
        assert simple_db['cluster'][1].env == 'prod'

    def test_should_fail_when_update_duplicate_name(self, simple_db):
        """name is unique."""
        c = MhCluster.get_by_id(simple_db['cluster'][0].id)
        with pytest.raises(DuplicateMhClusterNameError) as e:
            c.update(name=simple_db['cluster'][1].name)
        assert 'duplicate mh-cluster name(%s)' % \
                simple_db['cluster'][1].name in str(e.value)

    def test_should_fail_when_update_not_updateable_fields(self, simple_db):
        """capture_agents is not updateable."""
        c = MhCluster.get_by_id(simple_db['cluster'][0].id)
        with pytest.raises(InvalidOperationError) as e:
            c.update(capture_agents=[simple_db['ca'][1]])
        assert 'not allowed to update mh_cluster fields: capture_agents' \
                in str(e.value)

    def test_should_fail_when_update_invalid_env(self, simple_db):
        """env values are restricted to cadash.inventory.models.MH_ENV."""
        c = MhCluster.get_by_id(simple_db['cluster'][0].id)
        with pytest.raises(InvalidMhClusterEnvironmentError):
            c.update(env='BriteClass')


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
