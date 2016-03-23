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
from cadash.inventory.errors import InvalidMhClusterEnvironmentError
import cadash.utils as utils


class Location(SurrogatePK, Model):
    """a room where a capture agent is installed."""

    __tablename__ = 'ca_location'
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    name = Column(db.String(80), unique=True, nullable=False)
    name_id = Column(db.String(80), unique=True, nullable=False)

    def __init__(self, name, **kwargs):
        """create instance."""
        db.Model.__init__(self, name=name, **kwargs)
        self.name_id = utils.clean_name(name)


class Ca(SurrogatePK, Model):
    """a capture agent."""

    __tablename__ = 'ca'
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    name = Column(db.String(80), unique=True, nullable=False)
    name_id = Column(db.String(80), unique=True, nullable=False)
    address = Column(db.String(124), unique=True, nullable=False)
    serial_number = Column(db.String(80), unique=True, nullable=True)

    def __init__(self, name, address, serial_number=None, **kwargs):
        """create instance."""
        db.Model.__init__(
                self, name=name, address=address,
                serial_number=serial_number, **kwargs)
        self.name_id = utils.clean_name(name)


class Vendor(SurrogatePK, Model):
    """a capture agent vendor."""

    __tablename__ = 'vendor'
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    name = Column(db.String(80), unique=False, nullable=False)
    name_id = Column(db.String(80), unique=True, nullable=False)
    model = Column(db.String(80), unique=False, nullable=False)

    def __init__(self, name, model, **kwargs):
        """create instance."""
        db.Model.__init__(self, name=name, model=model, **kwargs)
        self.name_id = "%s_%s" % (utils.clean_name(name), utils.clean_name(model))


class MhCluster(SurrogatePK, Model):
    """a mh cluster that a capture agent pull schedule from."""

    __tablename__ = 'mhcluster'
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    name = Column(db.String(80), unique=True, nullable=False)
    name_id = Column(db.String(80), unique=True, nullable=False)
    admin_host = Column(db.String(124), unique=True, nullable=False)
    env = Column(db.String(80), unique=False, nullable=False)

    def __init__(self, name, admin_host, env, **kwargs):
        """create instance."""
        db.Model.__init__(self, name=name, admin_host=admin_host,
                env=MhCluster.get_valid_env(env), **kwargs)
        self.name_id = utils.clean_name(name)


    @staticmethod
    def get_valid_env(env):
        """returns valid env value: ['prod'|'dev'|'stage']."""
        environment = env.lower()
        if environment in ['prod', 'dev', 'stage']:
            return environment
        raise InvalidMhClusterEnvironmentError(
                'mh cluster env value not in [prod, dev, stage]: %s' % env)
