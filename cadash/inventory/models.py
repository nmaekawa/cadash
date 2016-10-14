# -*- coding: utf-8 -*-
"""capture agent models."""

import datetime as dt
import json
import pytz

from cadash.database import Column
from cadash.database import Model
from cadash.database import NameIdMixin
from cadash.database import SurrogatePK
from cadash.database import db
from cadash.database import relationship
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
from cadash.inventory.errors import InvalidEmptyValueError
from cadash.inventory.errors import InvalidJsonValueError
from cadash.inventory.errors import InvalidMhClusterEnvironmentError
from cadash.inventory.errors import InvalidOperationError
from cadash.inventory.errors import InvalidTimezoneError
from cadash.inventory.errors import MissingVendorError
import cadash.utils as utils

CA_ROLES = frozenset([u'primary', u'secondary', u'experimental'])
MH_ENVS = frozenset([u'prod', u'dev', u'stage'])
UPDATEABLE_CA_FIELDS = frozenset([
        u'name', u'address', u'serial_number', u'capture_card_id',
        u'username', u'password'])
UPDATEABLE_CLUSTER_FIELDS = frozenset([
        u'name', u'admin_host', u'env',
        u'username', u'password'])
UPDATEABLE_LOCATION_FIELDS = frozenset([u'name'])
UPDATEABLE_VENDOR_FIELDS = frozenset([u'name', u'model'])
UPDATEABLE_VENDOR_CONFIG_FIELDS = frozenset([
        u'touchscreen_timeout_secs', u'touchscreen_allow_recording',
        u'maintenance_permanent_logs', u'firmware_version',
        u'source_deinterlacing', u'datetime_timezone', u'datetime_ntpserver'])
UPDATEABLE_LOCATION_CONFIG_FIELDS = frozenset([
        u'primary_pr_vconnector', u'primary_pr_vinput',
        u'primary_pn_vconnector', u'primary_pn_vinput',
        u'secondary_pr_vconnector', u'secondary_pr_vinput',
        u'secondary_pn_vconnector', u'secondary_pn_vinput'])
UPDATEABLE_EPIPHAN_RECORDER_FIELDS = frozenset([
        u'recorder_id_in_device', u'ouput_format',
        u'size_limit_in_kbytes', u'time_limit_in_minutes'])
UPDATEABLE_EPIPHAN_CHANNEL_FIELDS = frozenset([
        u'stream_cfg', u'channel_id_in_device',
        u'audio', u'audiobitrate', u'audiochannels', u'audiopreset',
        u'autoframesize', u'codec', u'fpslimit', u'framesize',
        u'vbitrate', u'vencpreset', u'vkeyframeinterval',
        u'vprofile', u'source_layout'])




class Location(SurrogatePK, NameIdMixin, Model):
    """a room where a capture agent is installed."""

    __tablename__ = 'location'
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    name = Column(db.String(80), unique=True, nullable=False)
    capture_agents = relationship('Role', back_populates='location')
    config = relationship('LocationConfig', back_populates='location', uselist=False)

    def __init__(self, name):
        """create instance."""
        if self._check_constraints(name=name):
            db.Model.__init__(self, name=name)
            cfg = LocationConfig.create(location=self)
            self.config = cfg

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
            c.delete()
        self.config.delete(commit)  # delete associated config
        return super(Location, self).delete(commit)

    def update(self, **kwargs):
        """override to check location constraints."""
        x = set(kwargs.keys()).difference(UPDATEABLE_LOCATION_FIELDS)
        if len(x):
            raise InvalidOperationError(
                    'not allowed to update location fields: %s' %
                    ', '.join(list(x)))
        if self._check_constraints(**kwargs):
            return super(Location, self).update(**kwargs)

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
        return True


class LocationConfig(SurrogatePK, Model):
    """configuration settings for location."""

    __tablename__ = 'location_config'
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    primary_pr_vconnector = Column(db.String(16), nullable=False, default='sdi')
    primary_pr_vinput = Column(db.String(16), nullable=False, default='a')
    primary_pn_vconnector = Column(db.String(16), nullable=False, default='sdi')
    primary_pn_vinput = Column(db.String(16), nullable=False, default='b')
    secondary_pr_vconnector = Column(db.String(16), nullable=False, default='sdi')
    secondary_pr_vinput = Column(db.String(16), nullable=False, default='a')
    secondary_pn_vconnector = Column(db.String(16), nullable=False, default='sdi')
    secondary_pn_vinput = Column(db.String(16), nullable=False, default='b')
    location_id = Column(db.Integer, db.ForeignKey('location.id'))
    location = relationship('Location', back_populates='config')

    def __repr__(self):
        return "{}_config".format(self.location.name)

    def __init__(self, location):
        """validate constraints and create instance."""
        # location already has configs?
        if bool(location.config):
            raise AssociationError(
                    'cannot associate location({}): already has configs({})'.format(
                    (location.name, location.config.id)))
        else:
            db.Model.__init__(self, location=location)

    def update(self, **kwargs):
        """override to check config constraints."""
        x = set(kwargs.keys()).difference(UPDATEABLE_LOCATION_CONFIG_FIELDS)
        if len(x) > 0:
            raise InvalidOperationError(
                'not allowed to update location config fields: {}'.format(
                        ', '.join(list(x)) ) )

        if self._check_constraints(**kwargs):
            return super(LocationConfig, self).update(**kwargs)

    def _check_constraints(self, **kwargs):
        """raise an error if args violate config constraints."""
        for k, value in kwargs.items():
            if not value or not value.strip():
                raise InvalidEmptyValueError(
                        'not allowed empty value for location config `{}`'.format(k))
        # TODO: changes in connectors cascade into changes in epiphan channel
        # source layout. just give a warning?
        return True


class Role(Model):
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

        db.Model.__init__(
                self, ca=ca, location=location,
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


class Ca(SurrogatePK, NameIdMixin, Model):
    """a capture agent."""

    __tablename__ = 'ca'
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    name = Column(db.String(80), unique=True, nullable=False)
    address = Column(db.String(128), unique=True, nullable=False)
    serial_number = Column(db.String(80), unique=True, nullable=True)
    capture_card_id = Column(db.String(80), nullable=True)
    username = Column(db.String(80), nullable=True)
    password = Column(db.String(80), nullable=True)
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


    def update(self, **kwargs):
        """override to check ca constraints."""
        x = set(kwargs.keys()).difference(UPDATEABLE_CA_FIELDS)
        if len(x) > 0:
            raise InvalidOperationError(
                    'not allowed to update ca fields: %s' % ', '.join(list(x)))

        if self._check_constraints(**kwargs):
            return super(Ca, self).update(**kwargs)


    def delete(self, commit=True):
        """override to undo all role relationships involving this ca."""
        self.role.delete()
        return super(Ca, self).delete(commit)

    def _check_constraints(self, **kwargs):
        """raise an error if args violate ca constraints."""
        for key, value in kwargs.items():
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
            if key == 'serial_number' and not value == self.serial_number:
                c = Ca.query.filter_by(serial_number=value).first()
                if c is not None:
                    raise DuplicateCaptureAgentSerialNumberError(
                            'duplicate ca serial_number(%s)' % value)
        return True


class Vendor(SurrogatePK, Model):
    """a capture agent vendor."""

    __tablename__ = 'vendor'
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    name = Column(db.String(80), unique=False, nullable=False)
    model = Column(db.String(80), unique=False, nullable=False)
    name_id = Column(db.String(128), unique=True, nullable=False)
    capture_agents = relationship('Ca', back_populates='vendor')
    config = relationship('VendorConfig', back_populates='vendor', uselist=False)

    def __init__(self, name, model):
        """create instance."""
        if self._check_constraints(name=name, model=model):
            db.Model.__init__(
                    self, name=name, model=model,
                    name_id=Vendor.computed_name_id(name, model))
            cfg = VendorConfig.create(vendor=self)
            self.config = cfg

    def __repr__(self):
        return self.name_id

    def delete(self, commit=True):
        """override to disable deletion of vendors."""
        raise InvalidOperationError('not allowed to delete `vendor`')

    def update(self, **kwargs):
        """override to check vendor constraints."""
        x = set(kwargs.keys()).difference(UPDATEABLE_VENDOR_FIELDS)
        if len(x) > 0:
            raise InvalidOperationError(
                    'not allowed to update vendor fields: %s' %
                    ', '.join(list(x)))

        if self._check_constraints(**kwargs):
            # update name,model in vendor model
            super(Vendor, self).update(commit=False, **kwargs)
            # persist name,model,name_id
            return super(Vendor, self).update(
                    name_id=self.computed_name_id(self.name, self.model))

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
        return True

    @classmethod
    def computed_name_id(cls, name, model):
        return '%s_%s' % (utils.clean_name(name), utils.clean_name(model))


class VendorConfig(SurrogatePK, Model):
    """configuration settings for vendors."""

    __tablename__ = 'vendor_config'
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    touchscreen_timeout_secs = Column(db.Integer, nullable=False, default=600)
    touchscreen_allow_recording = Column(db.Boolean, nullable=False, default=False)
    maintenance_permanent_logs = Column(db.Boolean, nullable=False, default=True)
    datetime_timezone = Column(db.String(80), nullable=False, default='US/Eastern')
    datetime_ntpserver = Column(db.String(128), nullable=False, default='0.pool.ntp.org')
    firmware_version = Column(db.String(80), nullable=False, default='3.15.3f')
    source_deinterlacing = Column(db.Boolean, nullable=False, default=True)
    vendor_id = Column(db.Integer, db.ForeignKey('vendor.id'))
    vendor = relationship('Vendor', back_populates='config')

    def __repr__(self):
        return "{}_config".format(self.vendor.name_id)

    def __init__(self, vendor):
        """validate constraints and create instance."""
        # vendor already has configs?
        if bool(vendor.config):
            raise AssociationError(
                    'cannot associate vendor({}): already has configs({})'.format(
                    (vendor.name_id, vendor.config.id)))
        else:
            db.Model.__init__(self, vendor=vendor)

    def delete(self, commit=True):
        """override to disable deletion of vendor configuration."""
        raise InvalidOperationError('not allowed to delete `vendor_config`')

    def update(self, **kwargs):
        """override to check config constraints."""
        x = set(kwargs.keys()).difference(UPDATEABLE_VENDOR_CONFIG_FIELDS)
        if len(x) > 0:
            raise InvalidOperationError(
                'not allowed to update vendor config fields: {}'.format(
                        ', '.join(list(x)) ) )

        if self._check_constraints(**kwargs):
            return super(VendorConfig, self).update(**kwargs)

    def _check_constraints(self, **kwargs):
        """raise an error if args violate config constraints."""
        if 'datetime_timezone' in kwargs.keys():
            if kwargs['datetime_timezone'] not in pytz.all_timezones:
                raise InvalidTimezoneError(
                        'invalid timezone ({})'.format(
                            kwargs['datetime_timezone']))
        return True  # no constraints to check


class MhCluster(SurrogatePK, NameIdMixin, Model):
    """a mh cluster that a capture agent pull schedule from."""

    __tablename__ = 'mhcluster'
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    name = Column(db.String(80), unique=True, nullable=False)
    admin_host = Column(db.String(128), unique=True, nullable=False)
    username = Column(db.String(80), nullable=True)
    password = Column(db.String(80), nullable=True)
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
        """override to check mh cluster constraints."""
        x = set(kwargs.keys()).difference(UPDATEABLE_CLUSTER_FIELDS)
        if len(x) > 0:
            raise InvalidOperationError(
                    'not allowed to update mh_cluster fields: %s' %
                    ', '.join(list(x)))

        if self._check_constraints(**kwargs):
            r = super(MhCluster, self).update(commit=False, **kwargs)
            # ensure persisted `env` value is valid
            if 'env' in kwargs.keys():
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


class RoleConfig(SurrogatePK, Model):
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



class EpiphanRecorder(SurrogatePK, Model):
    """recorder configuration for an epiphan-pearl CA."""

    __tablename__ = 'epiphan_recorder'
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    name = Column(db.String(80), nullable=False)
    recorder_id_in_device = Column(db.Integer, nullable=False, default=9999)
    epiphan_config_id = Column(db.Integer, db.ForeignKey('epiphan_config.id'))
    epiphan_config = relationship('RoleConfig', back_populates='recorders')

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

    def update(self, **kwargs):
        """override to check recorder constraints."""
        x = set(kwargs.keys()).difference(UPDATEABLE_EPIPHAN_RECORDER_FIELDS)
        if len(x) > 0:
            raise InvalidOperationError(
                    'not allowed to update epiphan_recorder fields: %s' %
                    ', '.join(list(x)))

        if self._check_constraints(**kwargs):
            return super(EpiphanRecorder, self).update(commit=False, **kwargs)

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
            if k == 'recorder_id_in_device':
                if value != 9999 and value in recorder_map_id.keys():
                    raise DuplicateEpiphanRecorderIdError(
                            'recorder_id_in_device({}) already config as ({}) in ca({}) - cannot update'.format(
                                value, recorder_map_id[value],
                                self.epiphan_config.ca.name))
        return True  # no constraint to check

class EpiphanChannel(SurrogatePK, Model):
    """channel configuration for an epiphan-pearl CA."""

    __tablename__ = 'epiphan_channel'
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    name = Column(db.String(80), nullable=False)
    channel_id_in_device = Column(db.Integer, nullable=False, default=9999)
    stream_cfg_id = Column(db.Integer, db.ForeignKey('akamai_config.id'))
    stream_cfg = relationship('AkamaiStreamingConfig', back_populates='channels')
    epiphan_config_id = Column(db.Integer, db.ForeignKey('epiphan_config.id'))
    epiphan_config = relationship('RoleConfig', back_populates='channels')

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

    def update(self, **kwargs):
        """override to check channel constraints."""
        x = set(kwargs.keys()).difference(UPDATEABLE_EPIPHAN_CHANNEL_FIELDS)
        if len(x) > 0:
            raise InvalidOperationError(
                'not allowed to update epiphan-channel fields: {}'.format(
                        ', '.join(list(x)) ) )
        if self._check_constraints(**kwargs):
            return super(EpiphanChannel, self).update(**kwargs)

    def _check_constraints(self, **kwargs):
        """raise an error if args violate config constraints."""
        channel_map_id = self.epiphan_config.map_channel_id_to_channel_name()
        channel_map_name = self.epiphan_config.map_channel_name_to_channel_id()

        for k, value in kwargs.items():
            if k == 'datetime_timezone':
                if kwargs['datetime_timezone'] not in pytz.all_timezones:
                    raise InvalidTimezoneError('invalid timezone ({})'.format(
                                value))
                next
            if k == 'name':
                if value in channel_map_name.keys():
                    raise DuplicateEpiphanChannelError(
                            'channel({}) already in ca({}) - cannot update'.format(
                                value, self.epiphan_config.ca.name))
                next
            if k == 'channel_id_in_device':
                if value != 9999 and value in channel_map_id.keys():
                    raise DuplicateEpiphanChannelIdError(
                            'channel_id_in_device({}) already config as ({}) in ca({}) - cannot update'.format(
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

class AkamaiStreamingConfig(SurrogatePK, Model):
    """configuration for streaming via akamai services."""

    __tablename__ = 'akamai_config'
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    name = Column(db.String(80), nullable=False)
    comment = Column(db.String(256), nullable=True)
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
        raise InvalidOperationError('not allowed update `akamai streaming config`')


class MhpearlConfig(SurrogatePK, Model):
    """configuration for dce custom mhpearl module that runs in epiphan-pearls."""

    __tablename__ = 'mhpearl_config'
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    comment = Column(db.String(256), nullable=True)
    epiphan_config_id = Column(db.Integer, db.ForeignKey('epiphan_config.id'))
    epiphan_config = relationship('RoleConfig', back_populates='mhpearl')

    # configs that cannot be derived from role relationships
    # live stream follow schedule on/off or always on?
    manage_live = Column(db.Boolean, nullable=False, default=False)

    # default is current production as of 05oct16
    mhpearl_version = Column(db.String(80), nullable=False, default='2.0.0')

    # akamai stream_id
    live_broadcast_key = Column(db.String(80), nullable=False, default='1')
    lowbr_broadcast_key = Column(db.String(80), nullable=False, default='1')

    # i think timeout to connect to matterhorn
    connecttimeout_in_sec = Column(db.Integer, nullable=False, default=60)

    # low transmission rate timeout
    low_speed_time_in_sec = Column(db.Integer, nullable=False, default=300)

    # max ingest before adding random delays
    max_ingest = Column(db.Integer, nullable=False, default=1)

    # max delay before ingest
    ingest_delay_in_sec = Column(db.Integer, nullable=False, default=90)
    # ingest retries
    number_of_retries = Column(db.Integer, nullable=False, default=5)

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

    def update(self, **kwargs):
        """override to check constraints."""
        if 'epiphan_config' in kwargs.keys():
            raise InvalidOperationError(
                    'cannot update epiphan_config associated to mhpearl_config({})'.format(
                        self.id))
        return super(MhpearlConfig, self).update(**kwargs)
