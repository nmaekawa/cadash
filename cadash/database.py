# -*- coding: utf-8 -*-
"""Database module, including the SQLAlchemy database object and DB-related utilities."""
import datetime
import json
from sqlalchemy.orm import relationship
from sqlalchemy.orm import validates

from cadash.compat import basestring
from cadash.extensions import db
import cadash.utils as utils

# Alias common SQLAlchemy names
Column = db.Column
relationship = relationship
validates = validates


class CRUDMixin(object):
    """Mixin that adds convenience methods for CRUD (create, read, update, delete) operations."""

    @classmethod
    def create(cls, **kwargs):
        """Create a new record and save it the database."""
        instance = cls(**kwargs)
        return instance.save()

    def update(self, commit=True, **kwargs):
        """Update specific fields of a record."""
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        return commit and self.save() or self

    def save(self, commit=True):
        """Save the record."""
        db.session.add(self)
        if commit:
            db.session.commit()
        return self

    def delete(self, commit=True):
        """Remove the record from the database."""
        db.session.delete(self)
        return commit and db.session.commit()


class Model(CRUDMixin, db.Model):
    """Base model class that includes CRUD convenience methods."""

    __abstract__ = True


# From Mike Bayer's "Building the app" talk
# https://speakerdeck.com/zzzeek/building-the-app
class SurrogatePK(object):
    """A mixin that adds a surrogate integer 'primary key' column named ``id`` to any declarative-mapped class."""

    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)

    @classmethod
    def get_by_id(cls, record_id):
        """Get record by ID."""
        if any(
                (isinstance(record_id, basestring) and record_id.isdigit(),
                 isinstance(record_id, (int, float))),
        ):
            return cls.query.get(int(record_id))
        return None


class CreatedDateMixin(object):
    """mixin to add a `create_at` datetime column."""
    __table_args__ = {'extend_existing': True}

    created_at = Column(db.DateTime,
            nullable=False,
            default=datetime.datetime.utcnow)


class NameIdMixin(object):
    """mixin that adds a name_id property as alphanum version of `name` column."""

    @property
    def name_id(self):
        """note that `name_id` might not be unique even when `name` is."""
        try:
            return utils.clean_name(self.name)
        except AttributeError:
            return None

    def __repr__(self):
        return self.name

class SettingsMixin(object):
    """mixin that adds a settings column to any declarative-mapped class.

    assumes main object has CRUDMixin as parent
    settings assumed to be a dict that can be shallow copied and it's saved
        internally as json
    last_udpate is also provided.
    """
    __table_args__ = {'extend_existing': True}


    _settings_json = Column('settings_json',
            db.UnicodeText, nullable=False, default=u'{}')
    _settings_last_update = Column('settings_last_update',
            db.DateTime, nullable=True)

    @property
    def settings_last_update(self):
        return self._settings_last_update

    @property
    def settings(self):
        return json.loads(self._settings_json)

    @settings.setter
    def settings(self, s):
        self._settings_json = json.dumps(s, ensure_ascii=False)
        self._settings_last_update = datetime.datetime.utcnow()


def reference_col(tablename, nullable=False, pk_name='id', **kwargs):
    """Column that adds primary key foreign key reference.

    Usage: ::

        category_id = reference_col('category')
        category = relationship('Category', backref='categories')
    """
    return db.Column(
        db.ForeignKey('{0}.{1}'.format(tablename, pk_name)),
        nullable=nullable, **kwargs)
