# -*- coding: utf-8 -*-
"""Tests for `models` in redunlive webapp."""
from datetime import datetime
import httpretty
import pytest
from epipearl import Epipearl

from cadash.inventory.models import Ca
from cadash.inventory.models import Location

class TestCaptureAgentModel(object):


    def test_create_ca_object(self):
        ca = Ca(name='fake-epiphan')
        assert ca.name == 'fake-epiphan'


    def test_create_location_object(self):
        loc = Location(name='room A')
        assert loc.name == 'room A'
