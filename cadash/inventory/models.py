# -*- coding: utf-8 -*-
"""capture agent models."""

import datetime as dt

from cadash.database import Column
from cadash.database import Model
from cadash.database import SurrogatePK
from cadash.database import db
from cadash.database import reference_col
from cadash.database import relationship
from cadash.database import validates
from cadash.errors import Error


class Location(SurrogatePK, Model):
    """a room where a capture agent is installed."""

    __tablename__ = 'ca_location'
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    name = Column(db.String(80), unique=True, nullable=False)


class Ca(SurrogatePK, Model):
    """a capture agent."""

    __tablename__ = 'ca'
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    name = Column(db.String(80), unique=True, nullable=False)
    serial_number = Column(db.String(80), unique=True, nullable=True)
    address = Column(db.String(124), unique=True, nullable=False)


class Vendor(SurrogatePK, Model):
    """a capture agent vendor."""

    __tablename__ = 'vendor'
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    name = Column(db.String(80), unique=False, nullable=False)
    model = Column(db.String(80), unique=False, nullable=False)


class MhCluster(SurrogatePK, Model):
    """a mh cluster that a capture agent pull schedule from."""

    __tablename__ = 'mhcluster'
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    name = Column(db.String(80), unique=True, nullable=False)
    admin_host = Column(db.String(124), unique=True, nullable=False)
    env = Column(db.String(80), unique=False, nullable=False)

    @validates('env')
    def validate_env(self, key, env):
        """validates that env value in ['prod'|'dev'|'stage']."""
        environment = env.lower()
        if environment in ['prod', 'dev', 'stage']:
            return environment
        raise InvalidMhClusterEnvironment(
                'mh cluster env value not in [prod, dev, stage]: %s' % env)
