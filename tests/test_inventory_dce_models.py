# -*- coding: utf-8 -*-
"""Tests for `models` in redunlive webapp."""
import json
import pytest

from cadash import utils
from cadash.inventory.dce_models import DceEpiphanCa
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


@pytest.mark.usefixtures('db', 'simple_db')
class TestDceCaConfigModel(object):
    """tests dce wrapper around role-config."""

    def test_create_config(self, simple_db):
        """create a dce ca config."""
        ca = simple_db['ca'][2]
        cfg = RoleConfig(role=ca.role)

        dce_cfg = DceEpiphanCa(ca_config=cfg)

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

        full_config = dce_cfg.get_epiphan_dce_config()
        assert json.dumps(full_config) == '{"ha": "ho"}'
