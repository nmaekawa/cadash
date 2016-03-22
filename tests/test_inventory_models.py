# -*- coding: utf-8 -*-
"""Tests for `models` in redunlive webapp."""
import datetime as dt
import httpretty
import pytest
from epipearl import Epipearl

from cadash.inventory.models import Ca
from cadash.inventory.models import Location

@pytest.mark.usefixtures('db')
class TestCaptureAgentModel(object):
    """capture agent tests."""

    def test_get_by_id(self):
        """get ca by id."""
        ca = Ca(name='fake-epiphan', address='fake-epiphan.blah.bloh.net')
        ca.save()
        retrieved = Ca.get_by_id(ca.id)
        assert retrieved == ca


    def test_created_at_defaults_to_datetime(self):
        """test creation date."""
        ca = Ca(name='fake-epiphan', address='fake-epiphan.blah.bloh.net')
        ca.save()
        assert bool(ca.created_at)
        assert isinstance(ca.created_at, dt.datetime)


@pytest.mark.usefixtures('db')
class TestLocationModel(object):
    """location tests."""

    def test_create_location_object(self):
        """get location by id."""
        loc = Location(name='room A')
        loc.save()
        retrieved = Location.get_by_id(loc.id)
        assert retrieved == loc


    def test_createt_at_defaults_to_datetime(self):
        """test creation date."""
        loc = Location(name='room A')
        loc.save()
        assert bool(loc.created_at)
        assert isinstance(loc.created_at, dt.datetime)
