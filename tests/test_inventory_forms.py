# -*- coding: utf-8 -*-
"""test inventory forms."""
import pytest

from cadash.inventory.forms import CaForm
from cadash.inventory.forms import LocationForm
from cadash.inventory.forms import MhClusterForm
from cadash.inventory.forms import VendorForm

from cadash.inventory.models import Location
from cadash.inventory.models import Vendor


@pytest.mark.usefixtures('db', 'simple_db')
class TestLocationForm(object):
    """location form."""

    def test_room_form(self, simple_db):
        """test room happy path."""
        form = LocationForm(name='dark_room')
        validate = form.validate()
        assert validate is True


@pytest.mark.usefixtures('db', 'simple_db')
class TestCaForm(object):
    """capture agent form."""

    def test_ca_form(self, simple_db):
        """test ca happy path."""
        form = CaForm(name='fake-capture-agent',
                address='http://fake.dce.harvard.edu',
                vendor_id=simple_db['ca'][0].vendor.id,
                serial_number='ABC')
        form.vendor_id.choices = \
                [(simple_db['vendor'].id, simple_db['vendor'].name_id)]
        validate = form.validate()
        assert validate is True


@pytest.mark.usefixtures('db', 'simple_db')
class TestMhClusterForm(object):
    """mh cluster form."""

    def test_cluster_form(self, simple_db):
        """test cluster happy path."""
        form = MhClusterForm(name='fake-cluster',
                admin_host='http://fake.dce.harvard.edu',
                env='dev')
        validate = form.validate()
        assert validate is True


@pytest.mark.usefixtures('db', 'simple_db')
class TestVendorClusterForm(object):
    """vendor form."""

    def test_vendor_form(self, simple_db):
        """test vendor happy path."""
        form = VendorForm(name='fake-vendor', model='shiny-model')
        validate = form.validate()
        assert validate is True
