# -*- coding: utf-8 -*-
"""factories to help in tests."""
from factory import PostGenerationMethodCall
from factory import Sequence
from factory.alchemy import SQLAlchemyModelFactory

from cadash.database import db
from cadash.inventory.models import Ca
from cadash.inventory.models import Location
from cadash.inventory.models import MhCluster
from cadash.inventory.models import Role
from cadash.inventory.models import Vendor


class BaseFactory(SQLAlchemyModelFactory):
    """base factory."""

    class Meta:
        """factory configuration."""
        abstract = True
        sqlalchemy_session = db.session


class CaFactory(BaseFactory):
    """capture agent factory."""
    name = Sequence(lambda n: 'ca%s' % n)
    address = Sequence(lambda n: 'http://ca%s.fake.test' %n)
    serial_number = Sequence(lambda n: '123456789%s' %n)

    class Meta:
        """factory configuration."""
        model = Ca


class LocationFactory(BaseFactory):
    """location factory."""
    name = Sequence(lambda n: 'room %s' % n)

    class Meta:
        """factory configuration."""
        model = Location


class MhClusterFactory(BaseFactory):
    """mh cluster factory."""
    name = Sequence(lambda n: 'cluster %s' % n)
    admin_host = Sequence(lambda n: 'http://cluster%s.fake.test' % n)
    env = 'dev'

    class Meta:
        """factory configuration."""
        model = MhCluster


class VendorFactory(BaseFactory):
    """vendor factory."""
    name = Sequence(lambda n: 'epiphan%s' % n)
    model = Sequence(lambda n: 'model%s' % n)

    class Meta:
        """factory configuration."""
        model = Vendor
