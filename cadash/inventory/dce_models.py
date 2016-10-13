# -*- coding: utf-8 -*-
"""capture agent models."""

from jinja2 import Template
import json

from cadash.inventory.errors import AssociationError
from cadash.inventory.errors import DuplicateAkamaiStreamIdError
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
from cadash.inventory.models import AkamaiStreamingConfig
from cadash.inventory.models import Ca
from cadash.inventory.models import Location
from cadash.inventory.models import LocationConfig
from cadash.inventory.models import MhCluster
from cadash.inventory.models import Role
from cadash.inventory.models import RoleConfig
from cadash.inventory.models import Vendor
from cadash.inventory.models import VendorConfig
import cadash.utils as utils

DCE_CHANNEL_CONFIGS = {
        'dce_live': {
            'flavor': 'live',
            'stream_cfg': None,
            'encodings': {
                'audiobitrate': 96,
                'framesize': '1920x1080',
                'vbitrate': 4000,
                },
            },
        'dce_live_lowbr': {
            'flavor': 'live',
            'stream_cfg': None,
            'encodings': {
                'audiobitrate': 64,
                'framesize': '960x270',
                'vbitrate': 250,
                },
            },
        'dce_pr': {
            'flavor': 'pr',
            'stream_cfg': None,
            'encodings': {
                'audiobitrate': 160,
                'framesize': '1280x720',
                'vbitrate': 9000,
                },
            },
        'dce_pn': {
            'flavor': 'pn',
            'stream_cfg': None,
            'encodings': {
                'audiobitrate': 160,
                'framesize': '1920x540',
                'vbitrate': 9000,
                },
            },
        }

_layout_single_channel_template = Template('''{
    "audio": [
        {
            "settings": {
                "source": "{{source_id}}.{{aconnector}}-{{ainput}}-audio"
            },
            "type": "source"
        }
    ],
    "background": "#000000",
    "nosignal": {
        "id": "default"
    },
    "video": [
        {
            "position": {
                "height": "100%",
                "keep_aspect_ratio": true,
                "left": "0%",
                "top": "0%",
                "width": "100%"
            },
            "settings": {
                "source": "{{source_id}}.{{vconnector}}-{{vinput}}"
            },
            "type": "source"
        }
    ]
}
''')

_layout_combined_channels_template = Template('''{
    "audio": [
        {
            "settings": {
                "source": "{{source_id}}.{{pr_aconnector}}-{{pr_ainput}}-audio"
            },
            "type": "source"
        }
    ],
    "nosignal": {
        "id": "default"
    },
    "background": "#000000",
    "video": [
        {
            "crop": {},
            "position": {
                "keep_aspect_ratio": true,
                "height": "100%",
                "width": "50%",
                "left": "0%",
                "top": "0%"
            },
            "settings": {
                "source": "{{source_id}}.{{pr_vconnector}}-{{pr_vinput}}"
            },
            "type": "source"
        },
        {
            "crop": {},
            "position": {
                "keep_aspect_ratio": true,
                "height": "100%",
                "width": "50%",
                "left": "50%",
                "top": "0%"
            },
            "settings": {
                "source": "{{source_id}}.{{pn_vconnector}}-{{pn_vinput}}"
            },
            "type": "source"
        }
    ]
}''')


class DceEpiphanConfig(Object):
    """a capture agent dce-custom config for epiphan-pearl.

    wrapper over RoleConfig to apply some DCE business logic
    on how to configure an epiphan-pearl capture agent.
    """

    def __init__(self, ca_config):
        """create instance, based on RoleConfig ca_config."""
        self.config = ca_config
        self.ca = self.config.ca
        self.role_name = self.ca.role.name
        self.vendor = self.ca.vendor
        self.vendor_cfg = self.vendor.config
        self.location = self.config.role.location
        self.location_cfg = self.location.config
        self.cluster = self.config.role.cluster
        self.channels = self.config.channels
        self.recorders = self.config.recorders
        self.mhpearl = self.config.mhpearl
        # for easier access to ca connectors
        self.conn = {
            'primary': {
                'pr': {
                    'vconnector': self.location.config.primary_pr_vconnector,
                    'vinput': self.location.config.primary_pr_vinput,
                    },
                'pn': {
                    'vconnector': self.location.config.primary_pn_vconnector,
                    'vinput': self.location.config.primary_pn_vinput,
                    },
                },
            'secondary': {
                'pr': {
                    'vconnector': self.location.config.secondary_pr_vconnector,
                    'vinput': self.location.config.secondary_pr_vinput,
                    },
                'pn': {
                    'vconnector': self.location.config.secondary_pn_vconnector,
                    'vinput': self.location.config.secondary_pn_vinput,
                    },
                },
            }
        self.channel_cfg = DCE_CHANNEL_CONFIGS.copy()


    def _config_dce_recorder(self):
        """create and config channels for a dce ca."""
        rec = EpiphanRecorder.create(
                name=self.location.name_id,
                epiphan_config=self.ca_config)
        # for now, defaults are enough!


    def _config_dce_channels(self):
        """create and config channels for a dce ca."""
        # populate channel_cfg with stream config for live channels
        self._find_stream_cfg()

        for channel_name in self.encodings.keys():
            # create channel in model
            chan = EpiphanChannel.create(
                    name=channel_name,
                    epiphan_config=self.ca_config,
                    stream_cfg=self.channel_cfg[channel_name]['stream_cfg'])

            params = {}
            # config layout for input sources
            flavor = self.channel_cfg[channel_name]['flavor']
            if flavor == 'live':
                connector = self.conn[self.role_name]
                l = _layout_combined_channels_template.render(
                        source_id=self.ca.capture_card_id,
                        pr_vconnector=connector['pr']['vconnector'],
                        pr_vinput=connector['pr']['vinput'],
                        pn_vconnector=connector['pn']['vconnector'],
                        pn_vinput=connector['pn']['vinput'],
                        pr_aconnector=connector['pr']['vconnector'],
                        pr_ainput=connector['pr']['vinput'])
            else:
                connector = self.conn[self.role_name][flavor]
                l = _layout_combined_channel_template.render(
                        source_id=self.ca.capture_card_id,
                        vconnector=connector['vconnector'],
                        vinput=connector['vinput'],
                        # assume that audio always come from presenter
                        aconnector=self.conn[self.role_name]['pr']['vconnector'],
                        ainput=self.conn[self.role_name]['pr']['vinput'])

            params['source_layout'] = l.replace(' ', '').replace('\n', '')
            params.update(self.channel_cfg[channel_name]['encodings'])
            chan.update(**params)


    def _find_stream_cfg(self):
        """define some criteria to pick stream config for live channels."""
        scfg_list = AkamaiStreamingConfig.query.all()
        stream_cfg = None
        for s in scfg_list:
            if 'prod' in s.name:
                stream_cfg = s
                break
        self.channel_cfg['dce_live']['stream_cfg'] = stream_cfg
        self.channel_cfg['dce_live_lowbr']['stream_cfg'] = stream_cfg

