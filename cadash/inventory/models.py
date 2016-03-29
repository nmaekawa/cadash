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
import cadash.utils as utils

# FIXME: make sure can't append a spurious value to this
CA_ROLES = ['primary', 'secondary', 'experimental']

class Location(SurrogatePK, NameIdMixin, Model):
    """a room where a capture agent is installed."""

    __tablename__ = 'location'
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    name = Column(db.String(80), unique=True, nullable=False)
    capture_agents = relationship('Role', back_populates='location')

    def __init__(self, name):
        """create instance."""
        self.name = name

    def get_ca_by_role(self, role_name):
        """return list of capture-agents with given role."""
        result = []
        for r in self.capture_agents:
            if r.name == role_name:
                result.append(r.ca)
        return result


class Role(Model):
    """role for a ca in a room."""

    __tablename__ = 'role'
    name = Column(db.String(16), nullable=False, primary_key=True)
    ca_id = Column(db.Integer, db.ForeignKey('ca.id'), primary_key=True)
    ca = relationship('Ca', back_populates='role')
    location_id = Column(db.Integer, db.ForeignKey('location.id'))
    location = relationship('Location', back_populates='capture_agents')
    cluster_id = Column(db.Integer, db.ForeignKey('mhcluster.id'))
    cluster = relationship('MhCluster',
            back_populates='capture_agents', uselist=False)
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)


    def __init__(self, ca_id, location_id, cluster_id, name, **kwargs):
        """validate constraints and create instance."""
        # role name is valid?
        role = name.lower()
        if role not in CA_ROLES:
            raise InvalidCaRoleError(
                    'invalid ca-role(%s) - valid values: [%s]' %
                    (role, ','.join(CA_ROLES)))

        # ca already has a role?
        ca = Ca.get_by_id(ca_id)
        if bool(ca.role):
            raise AssociationError(
                    'cannot associate ca(%s): already has a role(%s)' %
                    (ca.name_id, ca.role))

        # location already has a ca with same role?
        l = Location.get_by_id(location_id)
        if role != 'experimental':
            duplicate = l.get_ca_by_role(role)
            if duplicate:
                raise AssociationError(
                        ('cannot associate location(%s): '
                        'already has ca with role(%s)') % (l.name_id, role))

        db.Model.__init__(self, ca_id=ca_id, location_id=location_id,
                cluster_id=cluster_id, name=role, **kwargs)


    def update(self, commit=True, **kwargs):
        """overrides to disable updates in role relationship."""
        raise InvalidOperationError('cannot update `role` relatioship')


    def __repr__(self):
        """represet instance as unique string."""
        return '<%s as %s in %s for %s>' % (self.ca.name_id,
                self.name, self.location.name_id, self.cluster.name_id)


class Ca(SurrogatePK, NameIdMixin, Model):
    """a capture agent."""

    __tablename__ = 'ca'
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    name = Column(db.String(80), unique=True, nullable=False)
    address = Column(db.String(124), unique=True, nullable=False)
    serial_number = Column(db.String(80), unique=True, nullable=True)
    vendor_id = Column(db.Integer, db.ForeignKey('vendor.id'), nullable=False)
    vendor = relationship('Vendor')
    role = relationship('Role', back_populates='ca', uselist=False)


class Vendor(SurrogatePK, Model):
    """a capture agent vendor."""

    __tablename__ = 'vendor'
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    name = Column(db.String(80), unique=False, nullable=False)
    model = Column(db.String(80), unique=False, nullable=False)
    capture_agents = relationship('Ca', back_populates='vendor')

    @property
    def name_id(self):
        return "%s_%s" % (utils.clean_name(self.name), utils.clean_name(self.model))

    def __repr__(self):
        return self.name_id


class MhCluster(SurrogatePK, NameIdMixin, Model):
    """a mh cluster that a capture agent pull schedule from."""

    __tablename__ = 'mhcluster'
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    name = Column(db.String(80), unique=True, nullable=False)
    admin_host = Column(db.String(124), unique=True, nullable=False)
    env = Column(db.String(80), unique=False, nullable=False)
    capture_agents = relationship('Role', back_populates='cluster')

    @validates('env')
    def validate_env(self, key, env):
        """returns valid env value: ['prod'|'dev'|'stage']."""
        if env is None:
            raise InvalidMhClusterEnvironmentError(
                    'missing mh cluster environment')

        environment = env.lower()
        if environment in ['prod', 'dev', 'stage']:
            return environment
        raise InvalidMhClusterEnvironmentError(
                'mh cluster env value not in [prod, dev, stage]: %s' % env)
