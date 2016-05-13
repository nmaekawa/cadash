# -*- coding: utf-8 -*-
"""epiphan configurer."""

from epipearl import Epipearl
class EpiphanSettingsHandler(object):
    """epiphan settings handler."""

    def __init__():
        """create instance."""
        self.client = Epipearl(base_url='http://fake.com',
                user='user', passwd='passwd')


# write a __factory__ for these dicts
#
# expected in settings for ca
ca = {
    'source_device_id': 'value', # maybe this is a inventory.Ca prop
    'firmware_version': 'value',
    'mhpearl_version': 'value',
    'pr': {
        'channel_id': '1',
        'layout': 'value', # "dce-factory default"
        },
    'pn': {
        'channel_id': '2',
        'layout': 'value',
        },
    'live': {
        'channel_id': '3',
        'layout': 'value',
        },
    'lowbr': {
        'channel_id': '4',
        'layout': 'value',
        },
    'pnpr': {
        'channel_id': 'm1',
        'layout': None,
        },
}

#
# expected in settings for epiphan vendor
vendor = {
    'ntp_server': {
        'address': 'value',
        'timezone': 'value',
        },
    'remote_support': {
        'permanent_logs': 'value',
        },
    'mhpearl': {
        'filesearch_range': 'value',
        }
}

#
# expected in settings for location
location = {
    'pr': {
        'connector': '[SDI|HDMI]',
        'framesize': 'value',
        'audio_bitrate' : 'value',
        'video_bitrate' : 'value', # check if needed
        },
    'pn': {
        'connector': '[SDI|HDMI]',
        'framesize': 'value',
        'video_bitrate' : 'value', # check if needed
        },
    'prpn': {
        'timelimit': 'value',
        'sizelimit': 'value',
        'output_format': 'value',
        },

    }
}

#
# expected in settings for cluster
cluster = {
     'rtmp_server_primary': {
        'url': 'value',
        'stream': 'value',
        'username': 'value',
        'password': 'value',
        },
     'rtmp_server_backup': {
        'url': 'value',
        'stream': 'value',
        'username': 'value',
        'password': 'value',
        },
     'mhpearl': {
         'url': 'value',
         'user': 'value',
         'password': 'value',
         'update_frequency': 'value',
         }

}
