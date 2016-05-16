# -*- coding: utf-8 -*-
"""default settings for dce epiphan."""

import logging

from cadash.caconf.epiphan.settings_factory \
        import SettingsFactory as EpiphanSettingsFactory

class SettingsFactory(object):
    """factory for ca dce settings for epiphans."""

    _settings = {
        # expected in settings for location
        'Location': {
            'pr': {
                'connector': 'SDI',
                'framesize': '1280x720',
                'audio_bitrate' : '128',
                'video_bitrate' : '9000', # check if needed
            },
            'pn': {
                'connector': 'SDI',
                'framesize': '1280x720',
                'video_bitrate' : '9000', # check if needed
            },
            'prpn': {
                'timelimit': '6:00:00',
                'sizelimit': '640000000',
                'output_format': 'AVI',
            },
        },

        # expected in settings for cluster
        'MhCluster': {
            'rtmp_server_primary': {
                'url': 'value',
                'stream': 'value',
                'username': 'CHANGEME',
                'password': 'CHANGEME',
            },
            'rtmp_server_backup': {
                'url': 'value',
                'stream': 'value',
                'username': 'CHANGEME',
                'password': 'CHANGEME',
            },
            'mhpearl': {
                'url': 'value',
                'user': 'CHANGEME',
                'password': 'CHANGEME',
                'update_frequency': '120',
            },
        },
    }

    @classmethod
    def settings_for_location(self):
        return self._settings['Location'].copy()

    @classmethod
    def settings_for_cluster(self):
        return self._settings['MhCluster'].copy()

    @classmethod
    def settings_for_vendor(self, vendor_name):
        if 'epiphan' in vendor_name.lower():
            return EpiphanSettingsFactory.settings_for_vendor()
        else:
            logger = logging.getLogger(__name__)
            logger.warning('settingsFactory(): unknown vendor(%s)' % vendor_name)
            return {}

    @classmethod
    def settings_for_ca(self, vendor_name):
        if 'epiphan' in vendor_name.lower():
            return EpiphanSettingsFactory.settings_for_ca()
        else:
            logger = logging.getLogger(__name__)
            logger.warning('settingsFactory(): unknown vendor(%s)' % vendor_name)
            return {}
