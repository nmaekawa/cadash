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
        form = LocationForm(
                name='dark_room',
                primary_pr_vconnector='sdi',
                primary_pr_vinput='a',
                primary_pn_vconnector='hdmi',
                primary_pn_vinput='b',
                secondary_pr_vconnector='hdmi',
                secondary_pr_vinput='a',
                secondary_pn_vconnector='hdmi',
                secondary_pn_vinput='b'
                )
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
class TestVendorForm(object):
    """vendor form."""

    def test_vendor_form(self, simple_db):
        """test vendor happy path."""
        form = VendorForm(
                name='fake-vendor', model='shiny-model',
                touchscreen_timeout_secs=90,
                touchscreen_allow_recording=True,
                maintenance_permanent_logs=False,
                datetime_timezone='Pacific/Fiji',
                datetime_ntpserver='8.8.8.8',
                firmware_version='some-crazy-number',
                source_deinterlacing=True)
        validate = form.validate()
        assert validate is True
