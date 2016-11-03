# -*- coding: utf-8 -*-
"""capture agent models."""

import datetime as dt
import json
import pytz

from cadash.database import db
from cadash.database import Column
from cadash.database import CRUDMixin
from cadash.database import Model
from cadash.database import NameIdMixin
from cadash.database import relationship
from cadash.database import SurrogatePK
from cadash.inventory.errors import AssociationError
from cadash.inventory.errors import DuplicateAkamaiStreamIdError
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
from cadash.inventory.errors import InvalidChannelNameForRecorderSetupError
from cadash.inventory.errors import InvalidEmptyValueError
from cadash.inventory.errors import InvalidJsonValueError
from cadash.inventory.errors import InvalidMhClusterEnvironmentError
from cadash.inventory.errors import InvalidOperationError
from cadash.inventory.errors import InvalidTimezoneError
from cadash.inventory.errors import MissingVendorError
import cadash.utils as utils

CA_ROLES = frozenset([u'primary', u'secondary', u'experimental'])
CA_STATES = frozenset([u'setup', u'active', u'inactive'])
MH_ENVS = frozenset([u'prod', u'dev', u'stage'])

class InventoryModel(CRUDMixin, db.Model):
    """base model class for cadash inventory."""

    __abstract__ = True
    __updateable_fields__ = frozenset([])

    @classmethod
    def updateable_fields(cls):
        return cls.__updateable_fields__

    def _check_constraints(self, **kwargs):
        """raise an error if args violate location constraints."""
        return True

    def update(self, commit=True, **kwargs):
        """override to check model constraints."""
        x = set(kwargs.keys()).difference(self.__class__.updateable_fields())
        if len(x) > 0:
            raise InvalidOperationError(
                'not allowed to update {} fields: {}'.format(
                        type(self).__name__,
                        ', '.join(list(x)) ) )
        if self._check_constraints(**kwargs):
            return super(InventoryModel, self).update(commit, **kwargs)


class Location(SurrogatePK, NameIdMixin, InventoryModel):
    """a room where a capture agent is installed."""

    __tablename__ = 'location'
    __updateable_fields__ = frozenset([
        u'primary_pr_vconnector', u'primary_pr_vinput',
        u'primary_pn_vconnector', u'primary_pn_vinput',
        u'secondary_pr_vconnector', u'secondary_pr_vinput',
        u'secondary_pn_vconnector',
        u'secondary_pn_vinput'])
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    name = Column(db.String(80), unique=True, nullable=False)
    primary_pr_vconnector = Column(db.String(16), nullable=False, default='sdi')
    primary_pr_vinput = Column(db.String(16), nullable=False, default='a')
    primary_pn_vconnector = Column(db.String(16), nullable=False, default='sdi')
    primary_pn_vinput = Column(db.String(16), nullable=False, default='b')
    secondary_pr_vconnector = Column(db.String(16), nullable=False, default='sdi')
    secondary_pr_vinput = Column(db.String(16), nullable=False, default='a')
    secondary_pn_vconnector = Column(db.String(16), nullable=False, default='sdi')
    secondary_pn_vinput = Column(db.String(16), nullable=False, default='b')

    capture_agents = relationship('Role', back_populates='location')

    def __init__(self, name):
        """create instance."""
        if self._check_constraints(name=name):
            db.Model.__init__(self, name=name)

    def get_ca(self):
        """return all capture agents installed in location."""
        result = [r.ca for r in self.capture_agents]
        return result

    def get_ca_by_role(self, role_name):
        """return list of capture-agents with given role."""
        result = [r.ca for r in self.capture_agents if r.name == role_name]
        return result

    def delete(self, commit=True):
        """override to undo all relationships involving this location."""
        for c in self.capture_agents:
            c.delete()  # delete roles associated with location
        return super(Location, self).delete(commit)

    def _check_constraints(self, **kwargs):
        """raise an error if args violate location constraints."""
        for k, value in kwargs.items():
            if k == 'name':
                if not value or not value.strip():
                    raise InvalidEmptyValueError(
                            'not allowed empty value for `name`')
                if not value == self.name:
                    l = Location.query.filter_by(name=value).first()
                    if l is not None:
                        raise DuplicateLocationNameError(
                                'duplicate location name(%s)' % value)
            if not value or not value.strip():
                raise InvalidEmptyValueError(
                    'not allowed empty value for location config `{}`'.format(k))
            # TODO: changes in connectors cascade into changes in epiphan
            # channelsource layout. just give a warning?
        return True


class Role(InventoryModel):
    """role for a ca in a room."""

    __tablename__ = 'role'
    name = Column(db.String(16), nullable=False)
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    ca_id = Column(db.Integer, db.ForeignKey('ca.id'), primary_key=True)
    ca = relationship('Ca', back_populates='role', uselist=False)
    location_id = Column(db.Integer, db.ForeignKey('location.id'))
    location = relationship(
            'Location', back_populates='capture_agents', uselist=False)
    cluster_id = Column(db.Integer, db.ForeignKey('mhcluster.id'))
    cluster = relationship(
            'MhCluster', back_populates='capture_agents', uselist=False)
    config_id = Column(db.Integer, db.ForeignKey('epiphan_config.id'))
    config = relationship('RoleConfig', back_populates='role', uselist=False)

    def __init__(self, ca, location, cluster, name):
        """validate constraints and create instance."""
        # role name is valid?
        role_name = name.lower()
        if role_name not in CA_ROLES:
            raise InvalidCaRoleError(
                    'invalid ca-role(%s) - valid values: [%s]' %
                    (role_name, ','.join(list(CA_ROLES))))
        # ca already has a role?
        if ca.role is not None:
            raise AssociationError(
                    'cannot associate ca(%s): already has a role(%s)' %
                    (ca.name_id, ca.role))
        # location already has a ca with same role?
        if role_name != 'experimental':
            duplicate = location.get_ca_by_role(role_name)
            if duplicate:
                raise AssociationError(
                    'cannot associate location(%s): already has ca with role(%s)'
                    % (location.name_id, role_name))

        super(Role, self).__init__(
                ca=ca, location=location,
                cluster=cluster, name=role_name, config=None)


    def __repr__(self):
        """represent instance as unique string."""
        return '<%s as %s in %s for %s>' % (
                self.ca.name_id,
                self.name, self.location.name_id, self.cluster.name_id)


    def update(self, commit=True, **kwargs):
        """override to disable updates in role relationship."""
        raise InvalidOperationError('not allowed update `role` relatioship')


    def delete(self, commit=True):
        """override to undo relationships."""
        try:
            self.config.delete()
        except AttributeError:
            pass  # non-existent config
        return super(Role, self).delete(commit)


class Ca(SurrogatePK, NameIdMixin, InventoryModel):
    """a capture agent."""

    __tablename__ = 'ca'
    __updateable_fields__ = frozenset([
        u'name', u'address', u'serial_number', u'capture_card_id',
        u'username', u'password', u'state'])
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    name = Column(db.String(80), unique=True, nullable=False)
    state = Column(db.String(16), nullable=False, default=u'setup')
    address = Column(db.String(128), unique=True, nullable=False)
    serial_number = Column(db.String(80), nullable=True, default='')
    capture_card_id = Column(db.String(80), nullable=True, default='')
    username = Column(db.String(80), nullable=True, default='')
    password = Column(db.String(80), nullable=True, default='')
    vendor_id = Column(db.Integer, db.ForeignKey('vendor.id'), nullable=False)
    vendor = relationship('Vendor')
    role = relationship('Role', back_populates='ca', uselist=False)

    def __init__(self, name, address, vendor_id, serial_number=None):
        """create instance."""
        if self._check_constraints(
                name=name,
                address=address, vendor_id=vendor_id,
                serial_number=serial_number):
            db.Model.__init__(
                    self, name=name, address=address,
                    vendor_id=vendor_id, serial_number=serial_number)

    @property
    def role_name(self):
        if bool(self.role):
            return self.role.name
        return None

    @property
    def location(self):
        if bool(self.role):
            return self.role.location
        return None

    @property
    def mh_cluster(self):
        if bool(self.role):
            return self.role.cluster
        return None

    def delete(self, commit=True):
        """override to undo all role relationships involving this ca."""
        self.role.delete()
        return super(Ca, self).delete(commit)

    def _valid_state(self, state):
        """check if ca state is a valid value."""
        return state in CA_STATES

    def update(self, commit=True, **kwargs):
        """override to check if state allows updates."""
        if self.state == u'inactive':
            if 'state' in kwargs and self._valid_state(kwargs['state']):
                return super(Ca, self).update(
                        commit=commit, state=kwargs['state'])
            else:
                raise InvalidOperationError(
                'not allowed to update CA({}) - state is "INACTIVE"'.format(
                    self.name))
        return super(Ca, self).update(commit=commit, **kwargs)

    def _check_constraints(self, **kwargs):
        """raise an error if args violate ca constraints."""
        for key, value in kwargs.items():
            # fail if state is invalid
            if key == 'state':
                if not self._valid_state(kwargs['state']):
                    raise InvalidCaStateError(
                            'invalid state({}) for ca({})'.format(
                                value, self.name))
                next

            # fail if unknown vendor
            if key == 'vendor_id':
                if not value:
                    raise InvalidEmptyValueError(
                            'not allowed empty value for `vendor_id`')
                if not value == self.vendor_id:
                    v = Vendor.get_by_id(value)
                    if v is None:
                        raise MissingVendorError(
                                'not in inventory: vendor_id(%i)' % value)
                next

            # fail if duplicate name
            if key == 'name':
                if not value or not value.strip():
                    raise InvalidEmptyValueError(
                            'not allowed empty value for `name`')
                if not value == self.name:
                    c = Ca.query.filter_by(name=value).first()
                    if c is not None:
                        raise DuplicateCaptureAgentNameError(
                                'duplicate ca name(%s)' % value)
                next

            # fail if duplicate address
            if key == 'address':
                if not value or not value.strip():
                    raise InvalidEmptyValueError(
                            'not allowed empty value for `address`')
                if not value == self.address:
                    c = Ca.query.filter_by(address=value).first()
                    if c is not None:
                        raise DuplicateCaptureAgentAddressError(
                                'duplicate ca address(%s)' % value)
                next

            # fail if duplicate serial_number
            if key == 'serial_number' and value != self.serial_number:
                c = Ca.query.filter_by(serial_number=value).first()
                if c is not None:
                    raise DuplicateCaptureAgentSerialNumberError(
                                    'duplicate ca serial_number(%s)' % value)
                next

        return True


class Vendor(SurrogatePK, InventoryModel):
    """a capture agent vendor."""

    __tablename__ = 'vendor'
    __updateable_fields__ = frozenset([
        u'touchscreen_timeout_secs', u'touchscreen_allow_recording',
        u'maintenance_permanent_logs', u'firmware_version',
        u'source_deinterlacing', u'datetime_timezone', u'datetime_ntpserver'])
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    name = Column(db.String(80), unique=False, nullable=False)
    model = Column(db.String(80), unique=False, nullable=False)
    name_id = Column(db.String(128), unique=True, nullable=False)
    touchscreen_timeout_secs = Column(db.Integer, nullable=False, default=600)
    touchscreen_allow_recording = Column(db.Boolean, nullable=False, default=False)
    maintenance_permanent_logs = Column(db.Boolean, nullable=False, default=True)
    datetime_timezone = Column(db.String(80), nullable=False, default='US/Eastern')
    datetime_ntpserver = Column(db.String(128), nullable=False, default='0.pool.ntp.org')
    firmware_version = Column(db.String(80), nullable=False, default='3.15.3f')
    source_deinterlacing = Column(db.Boolean, nullable=False, default=True)

    capture_agents = relationship('Ca', back_populates='vendor')

    def __init__(self, name, model):
        """create instance."""
        if self._check_constraints(name=name, model=model):
            db.Model.__init__(
                    self, name=name, model=model,
                    name_id=Vendor.computed_name_id(name, model))

    def __repr__(self):
        return self.name_id

    def delete(self, commit=True):
        """override to disable deletion of vendors."""
        raise InvalidOperationError('not allowed to delete `vendor`')

    def _check_constraints(self, **kwargs):
        """raise an error if args violate vendor constraints."""
        n = kwargs['name'] if 'name' in kwargs.keys() else self.name
        m = kwargs['model'] if 'model' in kwargs.keys() else self.model
        nm = Vendor.computed_name_id(n, m)
        if not nm == self.name_id:
            v = Vendor.query.filter_by(name_id=nm).first()
            if v is not None:
                raise DuplicateVendorNameModelError(
                        'duplicate vendor name_model(%s)' % nm)

        if 'datetime_timezone' in kwargs.keys():
            if kwargs['datetime_timezone'] not in pytz.all_timezones:
                raise InvalidTimezoneError(
                        'invalid timezone ({})'.format(
                            kwargs['datetime_timezone']))
        return True

    @classmethod
    def computed_name_id(cls, name, model):
        return '%s_%s' % (utils.clean_name(name), utils.clean_name(model))


class MhCluster(SurrogatePK, NameIdMixin, InventoryModel):
    """a mh cluster that a capture agent pull schedule from."""

    __tablename__ = 'mhcluster'
    __updateable_fields__ = frozenset([
        u'admin_host', u'env', u'username', u'password'])
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    name = Column(db.String(80), unique=True, nullable=False)
    admin_host = Column(db.String(128), unique=True, nullable=False)
    username = Column(db.String(80), nullable=True, default='')
    password = Column(db.String(80), nullable=True, default='')
    env = Column(db.String(80), unique=False, nullable=False)
    capture_agents = relationship('Role', back_populates='cluster')


    def __init__(self, name, admin_host, env):
        """create instance."""
        environment = self._get_valid_env(env)
        if self._check_constraints(name=name, admin_host=admin_host):
            db.Model.__init__(
                    self, name=name, admin_host=admin_host, env=environment)

    def get_ca(self):
        """return all capture agents configured for this cluster."""
        result = [r.ca for r in self.capture_agents]
        return result

    def get_ca_by_role(self, role_name):
        """return list of capture-agents with given role."""
        result = [r.ca for r in self.capture_agents if r.name == role_name]
        return result

    def delete(self, commit=True):
        """override to undo all role relationships involving this cluster."""
        for c in self.capture_agents:
            c.delete()
        return super(MhCluster, self).delete(commit)

    def update(self, **kwargs):
        """override to normalize env field."""
        super(MhCluster, self).update(commit=False, **kwargs)
        # ensure persisted `env` value is valid
        if 'env' in kwargs:
            self.env = self._get_valid_env(kwargs['env'])
        return self.save()

    def _check_constraints(self, **kwargs):
        """raise an error if args violate mh cluster constraints."""
        for k, value in kwargs.items():
            if k == 'name':
                if not value:
                    raise InvalidEmptyValueError(
                            'not allowed empty value for `name`')
                if not value == self.name:
                    c = MhCluster.query.filter_by(name=value).first()
                    if c is not None:
                        raise DuplicateMhClusterNameError(
                                'duplicate mh_cluster name(%s)' % value)
                next

            if k == 'admin_host':
                if not value:
                    raise InvalidEmptyValueError(
                            'not allowed empty value for `admin_host`')
                if not value == self.admin_host:
                    c = MhCluster.query.filter_by(admin_host=value).first()
                    if c is not None:
                        raise DuplicateMhClusterAdminHostError(
                                'duplicate mh_cluster admin host(%s)' % value)
                next
        return True

    def _get_valid_env(self, env=None):
        """return valid env value: ['prod'|'dev'|'stage']."""
        if env is None:
            raise InvalidMhClusterEnvironmentError(
                    'missing mh cluster environment')
        environment = env.lower()
        if environment in MH_ENVS:
            return environment
        raise InvalidMhClusterEnvironmentError(
                'mh cluster env value not in [{}]: {}'.format(
                    ','.join(list(MH_ENVS)), env))


class RoleConfig(SurrogatePK, InventoryModel):
    """config specific for epiphan-pearl."""

    __tablename__ = 'epiphan_config'
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    role = relationship('Role', back_populates='config', uselist=False)

    channels = relationship('EpiphanChannel', back_populates='epiphan_config')
    recorders = relationship('EpiphanRecorder', back_populates='epiphan_config')
    mhpearl = relationship('MhpearlConfig', back_populates='epiphan_config', uselist=False)

    def __init__(self, role):
        """create instance."""
        if role.config is not None:
            raise AssociationError(
                    'cannot associate epiphan-config to ca({}): already has a config({})'.format(
                        role.ca.id, role.config.id))
        db.Model.__init__(self, role=role)

    @property
    def ca(self):
        """return the corresponding ca for associated role."""
        return self.role.ca

    def map_channel_id_to_channel_name(self):
        """return a dict with key-value == channel_id_in_device:channel_name."""
        channel_map = {}
        try:  # beware that ids in device are defaulted to '0'
            channel_map = {c.channel_id_in_device: c.name for c in self.channels}
        except TypeError:
            # no channels for this ca
            pass
        return channel_map

    def map_channel_name_to_channel_id(self):
        """return a dict with key-value == channel_name:channel_id_in_device."""
        channel_map = {}
        try:
            channel_map = {c.name: c.channel_id_in_device for c in self.channels}
        except TypeError:
            # no channels for this ca
            pass
        return channel_map

    def map_recorder_id_to_recorder_name(self):
        """return a dict with key-value == recorder_id_in_device:recorder_name."""
        recorder_map = {}
        try:  # beware that ids in device are defaulted to '0'
            recorder_map = {r.recorder_id_in_device: r.name for r in self.recorders}
        except TypeError:
            # no recorders for this ca
            pass
        return recorder_map

    def map_recorder_name_to_recorder_id(self):
        """return a dict with key-value == channel_name:channel_id_in_device."""
        recorder_map = {}
        try:
            recorder_map = {r.name: r.recorder_id_in_device for r in self.recorders}
        except TypeError:
            # no recorders for this ca
            pass
        return recorder_map

    def delete(self):
        """remove relationships."""
        try:
            for chan in self.channels:
                chan.delete()
        except TypeError:
            pass  # no channels in ca
        try:
            for rec in self.recorders:
                rec.delete()
        except TypeError:
            pass  # no recorders in ca
        if self.mhpearl is not None:
            self.mhpearl.delete()
        return super(RoleConfig, self).delete()


association_recorder_channel_table = db.Table(
        'association_recorder_table',
        db.Column(
            'recorder_id', db.Integer,
            db.ForeignKey('epiphan_recorder.id')),
        db.Column(
            'channel_id', db.Integer,
            db.ForeignKey('epiphan_channel.id')))


class EpiphanRecorder(SurrogatePK, InventoryModel):
    """recorder configuration for an epiphan-pearl CA."""

    __tablename__ = 'epiphan_recorder'
    __updateable_fields__ = frozenset([
        u'recorder_id_in_device', u'output_format',
        u'size_limit_in_kbytes', u'time_limit_in_minutes',
        u'channels'])
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    name = Column(db.String(80), nullable=False)
    # assuming we'll never have more than 99998 recorders in a CA
    recorder_id_in_device = Column(db.Integer, nullable=False, default=99999)
    epiphan_config_id = Column(db.Integer, db.ForeignKey('epiphan_config.id'))
    epiphan_config = relationship('RoleConfig', back_populates='recorders')
    channels_setup = relationship(
            'EpiphanChannel',
            secondary=association_recorder_channel_table,
            back_populates='recorders')

    # media recording configurations
    output_format = Column(db.String(16), nullable=False, default='avi')
    size_limit_in_kbytes = Column(db.Integer, nullable=False, default=64000000)
    time_limit_in_minutes = Column(db.Integer, nullable=False, default=360)

    def __init__(self, name, epiphan_config):
        """create instance."""
        recorder_map_name = epiphan_config.map_recorder_name_to_recorder_id()
        if name in recorder_map_name.keys():
            raise DuplicateEpiphanRecorderError(
                    'recorder({}) already in ca({})'.format(
                        name, epiphan_config.ca.name))
        db.Model.__init__(self, name=name, epiphan_config=epiphan_config)

    @property
    def channels(self):
        """list of channel.name in the channels_setup."""
        return [c.name for c in self.channels_setup]
    @channels.setter
    def channels(self, channel_list):
        """set channel instance per list of channel names."""
        # integrity test: channel_list must contain names of channels that are
        # configured in the same CA as this recorder
        all_channels_in_ca = [c.name for c in self.epiphan_config.channels]
        for c in channel_list:
            if c not in all_channels_in_ca:
                # bad attempt to keep a line under 79 chars...
                msg = 'cannot setup channel({}) in recorder({}),'.format(
                        c, self.name) + 'not a channel in ca({})'.format(
                                self.epiphan_config.ca_name)
                raise InvalidChannelNameForRecorderSetupError(msg)

        c_list = []  # list of actual channel objects
        for chan in self.epiphan_config.channels:
            if chan.name in channel_list:
                c_list.append(chan)
        self.channels_setup = c_list

    def _check_constraints(self, **kwargs):
        """raise an error if args violate epiphan recorder constraints."""
        recorder_map_id = self.epiphan_config.map_recorder_id_to_recorder_name()
        recorder_map_name = self.epiphan_config.map_recorder_name_to_recorder_id()
        for k, value in kwargs.items():
            if k == 'name':
                if value in recorder_map_name.keys():
                    raise DuplicateEpiphanRecorderError(
                            'recorder({}) already in ca({}) - cannot update.'.format(
                                value, self.epiphan_config.ca.name))
            if k == 'recorder_id_in_device' \
                    and self.recorder_id_in_device != value \
                    and value != 99999 and value in recorder_map_id.keys():
                        raise DuplicateEpiphanRecorderIdError(
                                'recorder_id_in_device({}) already config as '
                                '({}) in ca({}) - cannot update'.format(
                                value, recorder_map_id[value],
                                self.epiphan_config.ca.name))
        return True  # no constraint to check


class EpiphanChannel(SurrogatePK, InventoryModel):
    """channel configuration for an epiphan-pearl CA."""

    __tablename__ = 'epiphan_channel'
    __updateable_fields__ = frozenset([
        u'stream_cfg', u'channel_id_in_device',
        u'audio', u'audiobitrate', u'audiochannels', u'audiopreset',
        u'autoframesize', u'codec', u'fpslimit', u'framesize',
        u'vbitrate', u'vencpreset', u'vkeyframeinterval',
        u'vprofile', u'source_layout'])
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    name = Column(db.String(80), nullable=False)
    # assuming we'll never have more than 99998 channels in a CA
    channel_id_in_device = Column(db.Integer, nullable=False, default=99999)
    stream_cfg_id = Column(db.Integer, db.ForeignKey('akamai_config.id'))
    stream_cfg = relationship('AkamaiStreamingConfig', back_populates='channels')
    epiphan_config_id = Column(db.Integer, db.ForeignKey('epiphan_config.id'))
    epiphan_config = relationship('RoleConfig', back_populates='channels')
    recorders = relationship(
            'EpiphanRecorder',
            secondary=association_recorder_channel_table,
            back_populates='channels_setup')

    # a/v encodings for a channel
    audio = Column(db.Boolean, nullable=False, default=True)
    audiobitrate = Column(db.Integer, nullable=False, default=96)
    audiochannels = Column(db.String(8), nullable=False, default='1')
    audiopreset = Column(db.String(80), nullable=False, default='libfaac;44100')
    autoframesize = Column(db.Boolean, nullable=False, default=False)
    codec = Column(db.String(80), nullable=False, default='h.264')
    fpslimit = Column(db.Integer, nullable=False, default=30)
    framesize = Column(db.String(80), nullable=False, default='1920x540')
    vbitrate = Column(db.Integer, nullable=False, default=4000)
    vencpreset = Column(db.String(8), nullable=False, default='5')
    vkeyframeinterval = Column(db.Integer, nullable=False, default=1)
    vprofile = Column(db.String(8), nullable=False, default='100')
    source_layout = Column(db.Text, nullable=False, default='{}')  # should be a valid json object

    def __init__(self, name, epiphan_config, stream_cfg=None):
        """create instance."""
        channel_map = epiphan_config.map_channel_name_to_channel_id()
        if name in channel_map.keys():
            raise DuplicateEpiphanChannelError(
                    'channel({}) already in ca({})'.format(
                        name, epiphan_config.ca.name))
        return db.Model.__init__(
                self, name=name, epiphan_config=epiphan_config, stream_cfg=stream_cfg)

    def _check_constraints(self, **kwargs):
        """raise an error if args violate config constraints."""
        channel_map_id = self.epiphan_config.map_channel_id_to_channel_name()
        channel_map_name = self.epiphan_config.map_channel_name_to_channel_id()

        for k, value in kwargs.items():
            if k == 'name':
                if value in channel_map_name.keys():
                    raise DuplicateEpiphanChannelError(
                            'channel({}) already in ca({}) - cannot update'.format(
                                value, self.epiphan_config.ca.name))
                next
            if k == 'channel_id_in_device' \
                    and self.channel_id_in_device != value \
                    and value != 99999 and value in channel_map_id.keys():
                        raise DuplicateEpiphanChannelIdError(
                                'channel_id_in_device({}) already config as '
                                '({}) in ca({}) - cannot update'.format(
                                    value, channel_map_id[value],
                                    self.epiphan_config.ca.name))
            if k == 'source_layout':
                try:
                    x = json.loads(value)
                except ValueError:
                    raise InvalidJsonValueError(
                            'source_layout({}...) cannot parse json'.format(value[:10]))
                try:
                    dummy = x['video']
                except (KeyError, TypeError):
                    raise InvalidJsonValueError(
                            'source_layout({}...) not valid json as source_layout object'.format(
                                value[:10]))
                next
        return True  # no constraints to check

class AkamaiStreamingConfig(SurrogatePK, InventoryModel):
    """configuration for streaming via akamai services."""

    __tablename__ = 'akamai_config'
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    name = Column(db.String(80), nullable=False)
    comment = Column(db.String(256), nullable=True, default='')
    channels = relationship('EpiphanChannel', back_populates='stream_cfg')

    stream_id = Column(db.String(80), nullable=False, unique=True)
    stream_user = Column(db.String(80), nullable=False)
    stream_password = Column(db.String(80), nullable=False)

    primary_url_jinja2_template = Column(db.String(128), nullable=False,
            default='rtmp://p.ep{{stream_id}}.i.akamaientrypoint.net/EntryPoint')
    secondary_url_jinja2_template = Column(db.String(128), nullable=False,
            default='rtmp://b.ep{{stream_id}}.i.akamaientrypoint.net/EntryPoint')
    stream_name_jinja2_template = Column(db.String(128), nullable=False,
            default='{{location_name}}-presenter-delivery.stream-{{framesize}}_1_200@{{stream_id}}')

    def __init__(self, name, stream_id, stream_user, stream_password):
        """create instance."""
        # check that no duplicate stream_ids
        scfg = AkamaiStreamingConfig.query.filter_by(stream_id=stream_id).first()
        if scfg is not None:
            raise DuplicateAkamaiStreamIdError(
                    'duplicate stream_id({}); already configured for ({})'.format(
                        stream_id, scfg.name))
        db.Model.__init__(
                self, name=name,
                stream_id=stream_id,
                stream_user=stream_user,
                stream_password=stream_password)

    def delete(self, commit=True):
        """override to check relationships before deletion."""
        if len(self.epiphan_channels) == 0:
            return super(AkamaiStreamingConfig, self).delete(commit)
        else:
            raise InvalidOperationError(
                    'cannot delete `akamai cfg` ({}): channels still configured'.format(
                        self.name))

    def update(self, commit=True, **kwargs):
        """override to disable updates in streaming config."""
        # TODO: implement update for usr/pwd and jinja2 templates
        raise InvalidOperationError('not allowed update `akamai streaming config`')


class MhpearlConfig(SurrogatePK, InventoryModel):
    """configuration for dce custom mhpearl module that runs in epiphan-pearls."""

    __tablename__ = 'mhpearl_config'
    __updateable_fields__ = frozenset([
        u'comment', u'mhpearl_version',
        u'file_search_range_in_sec', u'update_frequency_in_sec',
        ])
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    comment = Column(db.String(256), nullable=True, default='')
    epiphan_config_id = Column(db.Integer, db.ForeignKey('epiphan_config.id'))
    epiphan_config = relationship('RoleConfig', back_populates='mhpearl')

    # configs that cannot be derived from role relationships
    # default is current production as of 05oct16
    mhpearl_version = Column(db.String(80), nullable=False, default='2.0.0')
    # seconds from scheduled start
    file_search_range_in_sec = Column(db.Integer, nullable=False, default=60)
    # schedule update frequency
    update_frequency_in_sec = Column(db.Integer, nullable=False, default=120)

    def __init__(self, epiphan_config):
        """create instance."""
        if epiphan_config.mhpearl is not None:
            raise AssociationError(
                    'cannot add configs to ca({}): already has configs({})'.format(
                        epiphan_config.ca.name, epiphan_config.mhpearl.id))
        else:
            db.Model.__init__(self, epiphan_config=epiphan_config)
