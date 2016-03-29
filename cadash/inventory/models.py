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
from cadash.inventory.errors import InvalidCaRoleError
from cadash.inventory.errors import InvalidMhClusterEnvironmentError
import cadash.utils as utils

class Location(SurrogatePK, NameIdMixin, Model):
    """a room where a capture agent is installed."""

    __tablename__ = 'location'
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    name = Column(db.String(80), unique=True, nullable=False)
    capture_agents = relationship('Role', back_populates='location')



class Role(SurrogatePK, NameIdMixin, Model):
    """role for a ca in a room."""

    __tablename__ = 'role'
    name = Column(db.String(16), nullable=False)
    ca_id = Column(db.Integer, db.ForeignKey('ca.id'))
    ca = relationship('Ca', back_populates='role')
    location_id = Column(db.Integer, db.ForeignKey('location.id'))
    location = relationship('Location', back_populates='capture_agents')
    cluster_id = Column(db.Integer, db.ForeignKey('mhcluster.id'))
    cluster = relationship('MhCluster',
            back_populates='capture_agents', uselist=False)
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)


class Ca(SurrogatePK, NameIdMixin, Model):
    """a capture agent."""

    __tablename__ = 'ca'
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    name = Column(db.String(80), unique=True, nullable=False)
    address = Column(db.String(124), unique=True, nullable=False)
    serial_number = Column(db.String(80), unique=True, nullable=True)
    vendor_id = Column(db.Integer, db.ForeignKey('vendor.id'))
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
