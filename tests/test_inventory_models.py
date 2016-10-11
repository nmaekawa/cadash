# -*- coding: utf-8 -*-
"""Tests for `models` in redunlive webapp."""
import datetime as dt
import json
import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.exc import SQLAlchemyError

from cadash import utils
from cadash.inventory.models import Ca
from cadash.inventory.models import EpiphanChannel
from cadash.inventory.models import EpiphanConfig
from cadash.inventory.models import EpiphanRecorder
from cadash.inventory.models import Location
from cadash.inventory.models import LocationConfig
from cadash.inventory.models import MhCluster
from cadash.inventory.models import MhpearlConfig
from cadash.inventory.models import Role
from cadash.inventory.models import Vendor
from cadash.inventory.errors import AssociationError
from cadash.inventory.errors import DuplicateCaptureAgentNameError
from cadash.inventory.errors import DuplicateCaptureAgentAddressError
from cadash.inventory.errors import DuplicateCaptureAgentSerialNumberError
from cadash.inventory.errors import DuplicateEpiphanChannelError
from cadash.inventory.errors import DuplicateEpiphanChannelIdError
from cadash.inventory.errors import DuplicateEpiphanRecorderError
from cadash.inventory.errors import DuplicateEpiphanRecorderIdError
from cadash.inventory.errors import DuplicateLocationNameError
from cadash.inventory.errors import DuplicateMhClusterAdminHostError
from cadash.inventory.errors import DuplicateMhClusterNameError
from cadash.inventory.errors import DuplicateVendorNameModelError
from cadash.inventory.errors import InvalidCaRoleError
from cadash.inventory.errors import InvalidEmptyValueError
from cadash.inventory.errors import InvalidJsonValueError
from cadash.inventory.errors import InvalidMhClusterEnvironmentError
from cadash.inventory.errors import InvalidOperationError
from cadash.inventory.errors import InvalidTimezoneError
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

    def test_update_ca_capture_card_id(self, simple_db):
        ca = Ca.get_by_id(simple_db['ca'][0].id)
        assert ca.capture_card_id is None
        ca.update(capture_card_id='D1P234567')
        assert ca.capture_card_id == 'D1P234567'


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

    def test_create_location_config(self):
        loc = Location.create(name='room with a view')
        retrieved = Location.get_by_id(loc.id)
        assert retrieved == loc
        assert loc.config is not None
        assert loc.config.primary_pr_vconnector == 'sdi'
        assert loc.config.primary_pr_vinput == 'a'
        assert loc.config.primary_pn_vconnector == 'sdi'
        assert loc.config.primary_pn_vinput == 'b'
        assert loc.config.secondary_pr_vconnector == 'sdi'
        assert loc.config.secondary_pr_vinput == 'a'
        assert loc.config.secondary_pn_vconnector == 'sdi'
        assert loc.config.secondary_pn_vinput == 'b'

    def test_update_location_config(self):
        loc = Location.create(name='room with a view')
        assert loc.config is not None
        assert loc.config.primary_pr_vconnector == 'sdi'
        assert loc.config.primary_pr_vinput == 'a'
        assert loc.config.primary_pn_vconnector == 'sdi'
        assert loc.config.primary_pn_vinput == 'b'
        assert loc.config.secondary_pr_vconnector == 'sdi'
        assert loc.config.secondary_pr_vinput == 'a'
        assert loc.config.secondary_pn_vconnector == 'sdi'
        assert loc.config.secondary_pn_vinput == 'b'

        loc.config.update(
                primary_pr_vconnector='hdmi',
                primary_pr_vinput='b',
                primary_pn_vconnector='vga',
                primary_pn_vinput='a',
                secondary_pr_vconnector='vga',
                secondary_pr_vinput='b',
                secondary_pn_vconnector='vga',
                secondary_pn_vinput='a'
                )
        assert loc.config.primary_pr_vconnector == 'hdmi'
        assert loc.config.primary_pr_vinput == 'b'
        assert loc.config.primary_pn_vconnector == 'vga'
        assert loc.config.primary_pn_vinput == 'a'
        assert loc.config.secondary_pr_vconnector == 'vga'
        assert loc.config.secondary_pr_vinput == 'b'
        assert loc.config.secondary_pn_vconnector == 'vga'
        assert loc.config.secondary_pn_vinput == 'a'

    def test_should_fail_when_update_config_not_updateable_field(self):
        loc = Location.create(name='room with a view')
        with pytest.raises(InvalidOperationError) as e:
            loc.config.update(location=None)
        assert 'not allowed to update location config fields: location' in str(e.value)

    def test_should_fail_when_update_config_field_to_None(self):
        loc = Location.create(name='room with a view')
        with pytest.raises(InvalidEmptyValueError) as e:
            loc.config.update(secondary_pn_vinput=None)
        assert 'not allowed empty value for location config' in str(e.value)


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

    def test_create_config(self):
        vendor = Vendor.create(name='epipoing', model='drumpf')
        retrieved = Vendor.get_by_id(vendor.id)
        assert retrieved == vendor
        assert vendor.config is not None
        assert vendor.config.touchscreen_timeout_secs == 600
        assert not vendor.config.touchscreen_allow_recording
        assert vendor.config.maintenance_permanent_logs
        assert vendor.config.datetime_timezone == 'US/Eastern'
        assert vendor.config.datetime_ntpserver == '0.pool.ntp.org'
        assert vendor.config.firmware_version == '3.15.3f'
        assert vendor.config.source_deinterlacing

    def test_should_fail_when_update_config_not_updateable_field(self):
        vendor = Vendor.create(name='epipoing', model='drumpf')
        retrieved = Vendor.get_by_id(vendor.id)
        assert retrieved == vendor
        with pytest.raises(InvalidOperationError) as e:
            vendor.config.update(vendor=None)
        assert 'not allowed to update vendor config fields: vendor' in str(e.value)

    def test_update_vendor_config(self):
        vendor = Vendor.create(name='epipoing', model='drumpf')
        retrieved = Vendor.get_by_id(vendor.id)
        assert retrieved == vendor
        assert vendor.config is not None
        assert vendor.config.touchscreen_timeout_secs == 600
        assert not vendor.config.touchscreen_allow_recording
        assert vendor.config.maintenance_permanent_logs
        assert vendor.config.datetime_timezone == 'US/Eastern'
        assert vendor.config.datetime_ntpserver == '0.pool.ntp.org'
        assert vendor.config.firmware_version == '3.15.3f'
        assert vendor.config.source_deinterlacing

        vendor.config.update(
                touchscreen_timeout_secs=345,
                maintenance_permanent_logs=False,
                datetime_timezone='US/Alaska',
                firmware_version='fake123',
                source_deinterlacing=False)
        assert vendor.config.touchscreen_timeout_secs == 345
        assert not vendor.config.touchscreen_allow_recording
        assert not vendor.config.maintenance_permanent_logs
        assert vendor.config.datetime_timezone == 'US/Alaska'
        assert vendor.config.datetime_ntpserver == '0.pool.ntp.org'
        assert vendor.config.firmware_version == 'fake123'
        assert not vendor.config.source_deinterlacing

    def test_should_fail_when_config_timezone_invalid(self):
        vendor = Vendor.create(name='epipoing', model='drumpf')
        assert vendor.config.datetime_timezone == 'US/Eastern'
        with pytest.raises(InvalidTimezoneError) as e:
            vendor.config.update(datetime_timezone='MiddleEarth/Gondor')
        assert 'invalid timezone (MiddleEarth/Gondor)' in str(e.value)


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
        assert 'duplicate mh_cluster name(%s)' % \
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

    def test_delete_role(self, simple_db):
        """test all role relationships are deleted."""
        role = simple_db['ca'][0].role
        ca = role.ca
        ca_role_name = role.name
        location = role.location
        cluster = role.cluster
        role.delete()
        assert ca.role is None
        ll = [x for x in location.capture_agents if x.ca.id == ca.id]
        assert len(ll) == 0
        cl = [x for x in cluster.capture_agents if x.ca.id == ca.id]
        assert len(cl) == 0


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
        """delete not allowed."""
        with pytest.raises(InvalidOperationError):
            simple_db['vendor'].delete()

    def test_delete_ca(self, simple_db):
        """delete ca and ca's associations."""
        ca_id = simple_db['ca'][0].id
        simple_db['ca'][0].delete()
        assert Ca.get_by_id(ca_id) is None

    def test_delete_vendor_config(self, simple_db):
        """delete config not allowed."""
        with pytest.raises(InvalidOperationError):
            simple_db['vendor'].config.delete()

    def test_delete_location_config(self):
        loc = Location.create(name='room with a view')
        assert loc.config is not None
        c = LocationConfig.get_by_id(loc.config.id)
        assert c is not None
        assert c == loc.config

        loc.delete()
        cfg = LocationConfig.get_by_id(c.id)
        assert cfg is None

    def test_delete_role_and_assoc(self, simple_db):
        """delete role just undo associations."""
        assert len(simple_db['room'][0].get_ca_by_role('experimental')) == 2
        assert len(simple_db['room'][0].get_ca()) == 3
        role = simple_db['ca'][0].role
        ca = simple_db['ca'][0]
        epi_config = ca.role.config

        chan1 = epi_config.channels[0]
        chan2 = epi_config.channels[1]
        rec1 = epi_config.recorders[0]
        rec2 = epi_config.recorders[1]
        mhcfg = epi_config.mhpearl

        role.delete()
        assert Role.query.filter_by(ca_id=ca.id).first() is None
        assert simple_db['ca'][0].id == ca.id
        assert simple_db['ca'][0].role_name == None
        assert simple_db['ca'][1].role_name == 'experimental'
        assert simple_db['ca'][2].role_name == 'primary'
        assert simple_db['ca'][2].location.name == simple_db['room'][0].name
        assert len(simple_db['room'][0].get_ca_by_role('experimental')) == 1
        assert len(simple_db['cluster'][0].get_ca()) == 2

        assert EpiphanConfig.get_by_id(epi_config.id) is None
        assert EpiphanChannel.get_by_id(chan1.id) is None
        assert EpiphanChannel.get_by_id(chan2.id) is None
        assert EpiphanRecorder.get_by_id(rec1.id) is None
        assert EpiphanRecorder.get_by_id(rec2.id) is None
        assert MhpearlConfig.get_by_id(mhcfg.id) is None


@pytest.mark.usefixtures('db', 'simple_db')
class TestEpiphanChannelModel(object):
    """test for channels and recorders."""

    def test_channel(self, simple_db):
        ca = simple_db['ca'][0]
        epi_config = ca.role.config
        assert len(epi_config.channels) == 2
        assert epi_config.channels[0].name == 'fake_channel'
        assert epi_config.channels[1].name == 'another_fake_channel'
        assert epi_config.channels[0].epiphan_config == epi_config
        assert epi_config.channels[0].stream_cfg == simple_db['stream_config']
        assert epi_config.map_channel_name_to_channel_id() == {
                'fake_channel': 0,
                'another_fake_channel': 0}
        assert epi_config.map_channel_id_to_channel_name() == {0: 'another_fake_channel'}

    def test_should_fail_when_add_duplicate_channel_name(self, simple_db):
        ca = simple_db['ca'][0]
        epi_config = ca.role.config
        with pytest.raises(DuplicateEpiphanChannelError) as e:
            chan = EpiphanChannel.create(name='fake_channel',
                    epiphan_config=epi_config, stream_cfg=simple_db['stream_config'])
        assert 'channel(fake_channel) already in ca({})'.format(
                epi_config.ca.name) in e.value

    def test_should_fail_when_add_duplicate_channel_id(self, simple_db):
        ca = simple_db['ca'][0]
        epi_config = ca.role.config
        epi_config.channels[0].update(channel_id_in_device=1)
        with pytest.raises(DuplicateEpiphanChannelIdError) as e:
            epi_config.channels[1].update(channel_id_in_device=1)
        assert 'channel_id_in_device(1) already config as (fake_channel) in ca({}) - cannot update'.format(
                epi_config.ca.name) in e.value

    def test_recorder(self, simple_db):
        ca = simple_db['ca'][0]
        epi_config = ca.role.config
        assert len(epi_config.recorders) == 2
        assert epi_config.recorders[0].name == 'recorder_fake'
        assert epi_config.recorders[1].name == 'recorder_fake_2'
        assert epi_config.recorders[0].epiphan_config == epi_config
        assert epi_config.map_recorder_name_to_recorder_id() == {
                'recorder_fake': 0,
                'recorder_fake_2': 0}
        assert epi_config.map_recorder_id_to_recorder_name() == {0: 'recorder_fake_2'}

    def test_should_fail_when_add_duplicate_recorder_name(self, simple_db):
        ca = simple_db['ca'][0]
        epi_config = ca.role.config
        with pytest.raises(DuplicateEpiphanRecorderError) as e:
            rec = EpiphanRecorder.create(name='recorder_fake_2', epiphan_config=epi_config)
        assert 'recorder(recorder_fake_2) already in ca({})'.format(epi_config.ca.name) in e.value

    def test_should_fail_when_add_duplicate_recorder_id(self, simple_db):
        ca = simple_db['ca'][0]
        epi_config = ca.role.config
        epi_config.recorders[0].update(recorder_id_in_device=1)
        with pytest.raises(DuplicateEpiphanRecorderIdError) as e:
            epi_config.recorders[1].update(recorder_id_in_device=1)
        assert 'recorder_id_in_device(1) already config as (recorder_fake) in ca({}) - cannot update'.format(
                epi_config.ca.name) in e.value

    def test_add_channel_layout(self, simple_db):
        epi_config = simple_db['ca'][0].role.config
        chan = epi_config.channels[0]
        assert chan.source_layout == '{}'
        slayout = {
                'audio': [
                    {
                        'settings': '{}.{}-{}-audio'.format(
                            epi_config.ca.capture_card_id,
                            epi_config.ca.role.location.config.primary_pr_vconnector,
                            epi_config.ca.role.location.config.primary_pr_vinput
                            ),
                        'type': 'source'
                        }
                    ],
                'background': '#000000',
                'nosignal': {
                    'id': 'default'
                    },
                'video': [
                    {
                        'position': {
                            'height': '100%',
                            'keep_aspect_ratio': True,
                            'left': '0%',
                            'top': '0%',
                            'width': '100%'
                            },
                        'settings': {
                            'source': '{}.{}-{}'.format(
                                epi_config.ca.capture_card_id,
                                epi_config.ca.role.location.config.primary_pr_vconnector,
                                epi_config.ca.role.location.config.primary_pr_vinput
                                )
                            },
                        'type': 'source'
                        }
                    ],
                }
        chan.update(source_layout=json.dumps(slayout))
        assert chan.source_layout != '{}'
        assert json.loads(chan.source_layout) == slayout

    def test_should_fail_when_layout_is_invalid_json(self, simple_db):
        epi_config = simple_db['ca'][0].role.config
        chan = epi_config.channels[0]
        assert chan.source_layout == '{}'
        with pytest.raises(InvalidJsonValueError) as e:
            chan.update(source_layout='{some non-json thing,}')
        assert 'cannot parse json' in e.value.message

    def test_should_fail_when_layout_is_invalid_layout_json(self, simple_db):
        epi_config = simple_db['ca'][0].role.config
        chan = epi_config.channels[0]
        assert chan.source_layout == '{}'
        with pytest.raises(InvalidJsonValueError) as e:
            chan.update(source_layout='{"some_key": "some value"}')
        assert 'not valid json as source_layout object' in e.value.message


@pytest.mark.usefixtures('db', 'simple_db')
class TestMhpearlConfigModel(object):
    """test for mhpearl configs."""

    def test_add_mhpearl_config(self, simple_db):
        ca = simple_db['ca'][0]
        epi_config = ca.role.config
        assert epi_config.mhpearl is not None
        assert epi_config.mhpearl.epiphan_config == epi_config
        assert epi_config.mhpearl.mhpearl_version == '2.0.0'

    def test_should_fail_adding_more_than_one_mhpearl_config(self, simple_db):
        ca = simple_db['ca'][0]
        epi_config = ca.role.config
        with pytest.raises(AssociationError) as e:
            cfg = MhpearlConfig.create(epiphan_config=epi_config)
        assert 'cannot add configs to ca({}): already has configs({})'.format(
                epi_config.ca.name, epi_config.mhpearl.id) in e.value

    def test_should_fail_when_updating_config_association(self, simple_db):
        ca = simple_db['ca'][0]
        epi_config = ca.role.config
        mh_cfg = epi_config.mhpearl
        with pytest.raises(InvalidOperationError) as e:
            mh_cfg.update(epiphan_config=epi_config)
        assert 'cannot update epiphan_config associated to mhpearl_config({})'.format(
                mh_cfg.id) in e.value
