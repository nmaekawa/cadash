# -*- coding: utf-8 -*-
"""capture agent models."""

import datetime as dt

from cadash.database import Column
from cadash.database import Model
from cadash.database import NameIdMixin
from cadash.database import SurrogatePK
from cadash.database import db
from cadash.database import reference_col
from cadash.database import relationship
from cadash.database import validates
from cadash.inventory.errors import AssociationError
from cadash.inventory.errors import InvalidCaRoleError
from cadash.inventory.errors import InvalidMhClusterEnvironmentError
from cadash.inventory.errors import InvalidOperationError
from cadash.inventory.errors import MissingVendorError
import cadash.utils as utils

# FIXME: make sure can't append a spurious value to this
CA_ROLES = [u'primary', u'secondary', u'experimental']
MH_ENVS = [u'prod', u'dev', u'stage']

class Location(SurrogatePK, NameIdMixin, Model):
    """a room where a capture agent is installed."""

    __tablename__ = 'location'
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    name = Column(db.String(80), unique=True, nullable=False)
    capture_agents = relationship('Role', back_populates='location')

    def __init__(self, name):
        """create instance."""
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
            c.delete()
        return super(Location, self).delete(commit)


class Role(Model):
    """role for a ca in a room."""

    __tablename__ = 'role'
    name = Column(db.String(16), nullable=False, primary_key=True)
    ca_id = Column(db.Integer, db.ForeignKey('ca.id'), primary_key=True)
    ca = relationship('Ca', back_populates='role')
    location_id = Column(db.Integer, db.ForeignKey('location.id'))
    location = relationship('Location',
            back_populates='capture_agents', uselist=False)
    cluster_id = Column(db.Integer, db.ForeignKey('mhcluster.id'))
    cluster = relationship('MhCluster',
            back_populates='capture_agents', uselist=False)
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)


    def __init__(self, ca, location, cluster, name):
        """validate constraints and create instance."""
        # role name is valid?
        role_name = name.lower()
        if role_name not in CA_ROLES:
            raise InvalidCaRoleError(
                    'invalid ca-role(%s) - valid values: [%s]' %
                    (role_name, ','.join(CA_ROLES)))

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
                        ('cannot associate location(%s): '
                        'already has ca with role(%s)') %
                        (location.name_id, role_name))

        db.Model.__init__(self, ca=ca, location=location,
                cluster=cluster, name=role_name)


    def __repr__(self):
        """represet instance as unique string."""
        return '<%s as %s in %s for %s>' % (self.ca.name_id,
                self.name, self.location.name_id, self.cluster.name_id)


    def update(self, commit=True, **kwargs):
        """overrides to disable updates in role relationship."""
        raise InvalidOperationError('cannot update `role` relatioship')


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


    def __init__(self, name, address, vendor, serial_number=None):
        """create instance."""
        # fail if unknown vendor

        # fail if duplicate name

        # fail if duplicate address

        # fail if duplicate serial_number
        db.Model.__init__(self, name=name, address=address,
                vendor=vendor, serial_number=serial_number)

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


    @classmethod
    def create(cls, **kwargs):
        """override to validate and throw custom errors."""

        return super(Ca, cls).create(**kwargs)


    def delete(self, commit=True):
        """override to undo all role relationships involving this ca."""
        self.role.delete()
        return super(Ca, self).delete(commit)


class Vendor(SurrogatePK, Model):
    """a capture agent vendor."""

    __tablename__ = 'vendor'
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    name = Column(db.String(64), unique=False, nullable=False)
    model = Column(db.String(64), unique=False, nullable=False)
    name_id = Column(db.String(128), unique=True, nullable=False)
    capture_agents = relationship('Ca', back_populates='vendor')

    def __init__(self, name, model):
        """create instance."""
        name_id = "%s_%s" % (utils.clean_name(name),
                utils.clean_name(model))
        db.Model.__init__(self, name=name, model=model, name_id=name_id)

    def __repr__(self):
        return '%s_%s' % (self.name, self.model)

    def delete(self, commit=True):
        """override to disable deletion of vendors."""
        raise InvalidOperationError('not allowed to delete `vendor`')


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
        db.Model.__init__(self, name=name, admin_host=admin_host,
                env=environment)


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


    def _get_valid_env(self, env):
        """returns valid env value: ['prod'|'dev'|'stage']."""
        if env is None:
            raise InvalidMhClusterEnvironmentError(
                    'missing mh cluster environment')

        environment = env.lower()
        if environment in MH_ENVS:
            return environment
        raise InvalidMhClusterEnvironmentError(
                'mh cluster env value not in [%s]: %s' %
                (','.join(MH_ENVS), env))
