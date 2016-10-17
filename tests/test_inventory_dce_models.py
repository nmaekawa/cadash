# -*- coding: utf-8 -*-
"""Tests for `models` in redunlive webapp."""
import json
import os
import pytest

from cadash import utils
from cadash.inventory.dce_models import DceConfigForEpiphanCa
from cadash.inventory.dce_models import DceConfigForEpiphanCaFactory
from cadash.inventory.models import Ca
from cadash.inventory.models import EpiphanChannel
from cadash.inventory.models import EpiphanRecorder
from cadash.inventory.models import Location
from cadash.inventory.models import LocationConfig
from cadash.inventory.models import MhCluster
from cadash.inventory.models import MhpearlConfig
from cadash.inventory.models import Role
from cadash.inventory.models import RoleConfig
from cadash.inventory.models import Vendor
from cadash.inventory.errors import AssociationError
from cadash.inventory.errors import DuplicateCaptureAgentNameError
from cadash.inventory.errors import DuplicateCaptureAgentAddressError
from cadash.inventory.errors import DuplicateCaptureAgentSerialNumberError
from cadash.inventory.errors import DuplicateEpiphanChannelError
from cadash.inventory.errors import DuplicateEpiphanChannelIdError
from cadash.inventory.errors import DuplicateEpiphanRecorderError
from cadash.inventory.errors import DuplicateEpiphanRecorderIdError
from cadash.inventory.errors import DuplicateLocationNameError
from cadash.inventory.errors import DuplicateMhClusterAdminHostError
from cadash.inventory.errors import DuplicateMhClusterNameError
from cadash.inventory.errors import DuplicateVendorNameModelError
from cadash.inventory.errors import InvalidCaRoleError
from cadash.inventory.errors import InvalidEmptyValueError
from cadash.inventory.errors import InvalidJsonValueError
from cadash.inventory.errors import InvalidMhClusterEnvironmentError
from cadash.inventory.errors import InvalidOperationError
from cadash.inventory.errors import InvalidTimezoneError
from cadash.inventory.errors import MissingVendorError


json_base_config_filename = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 'base_dce_ca_config.json')

@pytest.mark.usefixtures('db', 'simple_db')
class TestDceCaConfigModel(object):
    """tests dce wrapper around role-config."""

    def test_create_config(self, simple_db):
        """create a dce ca config."""
        ca = simple_db['ca'][2]
        dce_cfg = DceConfigForEpiphanCaFactory.retrieve(ca_id=ca.id)
        cfg = ca.role.config

        assert cfg is not None
        assert dce_cfg is not None
        assert dce_cfg.role_name == ca.role.name
        assert dce_cfg.location == ca.role.location
        assert dce_cfg.location_cfg == ca.role.location.config
        assert dce_cfg.vendor_cfg == ca.vendor.config
        assert dce_cfg.vendor == ca.vendor
        assert dce_cfg.cluster == ca.role.cluster
        assert len(dce_cfg.recorders) == 1
        assert len(dce_cfg.channels) == 4
        assert dce_cfg.recorders[0].name == dce_cfg.location.name_id


    def test_get_ca_config(self, simple_db):
        """check that config is correct."""
        ca = simple_db['ca'][2]
        dce_cfg = DceConfigForEpiphanCaFactory.retrieve(ca_id=ca.id)
        cfg = ca.role.config

        # must update channel/recorder ids
        i = 1
        for rec in sorted(cfg.recorders, key=lambda rec: rec.name):
            rec.recorder_id_in_device = i
            i += 1
        for chan in sorted(cfg.channels, key=lambda chan: chan.name):
            chan.channel_id_in_device = i
            i += 1

        full_config = dce_cfg.epiphan_dce_config
        with open(json_base_config_filename, 'r') as f:
            base_config = json.load(f)
        assert full_config == base_config

