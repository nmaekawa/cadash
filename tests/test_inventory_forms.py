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

    def test_duplicate_room(self, simple_db):
        """should fail if duplicate room."""
        form = LocationForm(name=simple_db['room'][0].name)
        validate = form.validate()
        assert validate is False
        assert 'location already in inventory' in form.name.errors


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


    def test_duplicate_serial_number(self, simple_db):
        """test serial_number is unique."""
        simple_db['ca'][0].serial_number = '1234567890'
        form = CaForm(name='fake-capture-agent',
                address='http://fake.dce.harvard.edu',
                vendor_id=simple_db['ca'][0].vendor.id,
                serial_number=simple_db['ca'][0].serial_number)
        form.vendor_id.choices = \
                [(simple_db['vendor'].id, simple_db['vendor'].name_id)]
        validate = form.validate()
        assert validate is False
        assert 'ca with same serial number already in inventory' in \
                form.serial_number.errors


    def test_duplicate_address(self, simple_db):
        """test address is unique."""
        form = CaForm(name='fake-capture-agent',
                address=simple_db['ca'][0].address,
                vendor_id=simple_db['ca'][0].vendor.id,
                serial_number='ABC')
        form.vendor_id.choices = \
                [(simple_db['vendor'].id, simple_db['vendor'].name_id)]
        validate = form.validate()
        assert validate is False
        assert 'ca with same address already in inventory' in \
                form.address.errors


    def test_duplicate_name(self, simple_db):
        """test name is unique."""
        form = CaForm(name=simple_db['ca'][0].name,
                address='http://fake.address.com',
                vendor_id=simple_db['ca'][0].vendor.id,
                serial_number='ABC')
        form.vendor_id.choices = \
                [(simple_db['vendor'].id, simple_db['vendor'].name_id)]
        validate = form.validate()
        assert validate is False
        assert 'ca with same name already in inventory' in \
                form.name.errors


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

    def test_duplicate_name(self, simple_db):
        """test cluster name is unique."""
        form = MhClusterForm(name=simple_db['cluster'][0].name,
                admin_host='http://fake.dce.harvard.edu',
                env='dev')
        validate = form.validate()
        assert validate is False
        assert 'cluster with same name already in inventory' in \
                form.name.errors

    def test_duplicate_admin_host(self, simple_db):
        """test cluster admin_host is unique."""
        form = MhClusterForm(name='fake-cluster',
                admin_host=simple_db['cluster'][0].admin_host,
                env='dev')
        validate = form.validate()
        assert validate is False
        assert 'cluster with same admin host address already in inventory' in \
                form.admin_host.errors


@pytest.mark.usefixtures('db', 'simple_db')
class TestVendorClusterForm(object):
    """vendor form."""

    def test_vendor_form(self, simple_db):
        """test vendor happy path."""
        form = VendorForm(name='fake-vendor', model='shiny-model')
        validate = form.validate()
        assert validate is True

    def test_duplicate_vendor_model(self, simple_db):
        """test vendor_model is unique."""
        form = VendorForm(name=simple_db['vendor'].name,
                model=simple_db['vendor'].model)
        validate = form.validate()
        assert validate is False
        assert 'vendor-model already in inventory' in form.name.errors
