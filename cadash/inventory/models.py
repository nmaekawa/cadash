# -*- coding: utf-8 -*-
"""capture agent models."""

import datetime as dt
import pytz

from cadash.database import Column
from cadash.database import Model
from cadash.database import NameIdMixin
from cadash.database import SurrogatePK
from cadash.database import db
from cadash.database import relationship
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
from cadash.inventory.errors import InvalidTimezoneError
from cadash.inventory.errors import MissingVendorError
import cadash.utils as utils

CA_ROLES = frozenset([u'primary', u'secondary', u'experimental'])
MH_ENVS = frozenset([u'prod', u'dev', u'stage'])
UPDATEABLE_CA_FIELDS = frozenset([u'name', u'address', u'serial_number'])
UPDATEABLE_CLUSTER_FIELDS = frozenset([u'name', u'admin_host', u'env'])
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
        return True


class Role(Model):
    """role for a ca in a room."""

    __tablename__ = 'role'
    name = Column(db.String(16), nullable=False)
    ca_id = Column(db.Integer, db.ForeignKey('ca.id'), primary_key=True)
    ca = relationship('Ca', back_populates='role')
    location_id = Column(db.Integer, db.ForeignKey('location.id'))
    location = relationship(
            'Location', back_populates='capture_agents', uselist=False)
    cluster_id = Column(db.Integer, db.ForeignKey('mhcluster.id'))
    cluster = relationship(
            'MhCluster', back_populates='capture_agents', uselist=False)
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)


    def __init__(self, ca, location, cluster, name):
        """validate constraints and create instance."""
        # role name is valid?
        role_name = name.lower()
        if role_name not in CA_ROLES:
            raise InvalidCaRoleError(
                    'invalid ca-role(%s) - valid values: [%s]' %
                    (role_name, ','.join(list(CA_ROLES))))
        # ca already has a role?
        if bool(ca.role):
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
                cluster=cluster, name=role_name)


    def __repr__(self):
        """represent instance as unique string."""
        return '<%s as %s in %s for %s>' % (
                self.ca.name_id,
                self.name, self.location.name_id, self.cluster.name_id)


    def update(self, commit=True, **kwargs):
        """override to disable updates in role relationship."""
        raise InvalidOperationError('not allowed update `role` relatioship')


class Ca(SurrogatePK, NameIdMixin, Model):
    """a capture agent."""

    __tablename__ = 'ca'
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    name = Column(db.String(80), unique=True, nullable=False)
    address = Column(db.String(128), unique=True, nullable=False)
    serial_number = Column(db.String(80), unique=True, nullable=True)
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
    name = Column(db.String(64), unique=False, nullable=False)
    model = Column(db.String(64), unique=False, nullable=False)
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
    datetime_timezone = Column(db.String(64), nullable=False, default='US/Eastern')
    datetime_ntpserver = Column(db.String(128), nullable=False, default='0.pool.ntp.org')
    firmware_version = Column(db.String(64), nullable=False, default='3.15.3f')
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
                'mh cluster env value not in [%s]: %s' %
                (','.join(list(MH_ENVS)), env))
