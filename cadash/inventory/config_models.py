# -*- coding: utf-8 -*-
"""capture agent config models."""


ecfg = {}

ecfg['channel_pr'] = {}
ecfg['channel_pn'] = {}
ecfg['recorder_prpn'] = {}
ecfg['channel_live'] = {}
ecfg['channel_lowbr'] = {}

channel = {}
channel['channelname']
channel['framesize']
channel['codec']
channel['vbitrate']
channel['vkeyframeinterval']
channel['vencpreset']
channel['vprofile']
channel['audio']
channel['audiopreset']
channel['audiobitrate']
channel['audiochannels']
channel['active_layout']
channel['/layouts/1:settings']
channel['/public/0:rtmp_url']
channel['/public/0:rtmp_username']
channel['/public/0:rtmp_password']
channel['/public/0:rtmp_stream']

recorder = {}
recorder['timelimit']
recorder['sizelimit']
recorder['output_format']
recorder['channels']
recorder['channelname']


ecfg['mhpearl_device_name'] = {}
ecfg['mhpearl_device_username'] = {}
ecfg['mhpearl_device_password'] = {}
ecfg['mhpearl_device_channel'] = {}
ecfg['mhpearl_device_live_channel'] = {}
ecfg['mhpearl_device_lowbr_channel'] = {}
ecfg['mhpearl_file_search_range'] = {}
ecfg['mhpearl_admin_server_url'] = {}
ecfg['mhpearl_admin_server_user'] = {}
ecfg['mhpearl_admin_server_passwd'] = {}
ecfg['mhpearl_update_frequency'] = {}
ecfg['mhpearl_backup_agent'] = {}

ecfg['ntp_server'] = 'server.x.com'
ecfg['ntp_timezone'] = 'US/Eastern'
ecfg['permanent_syslog']

ecfg['touchscreen_recordctl'] = 'on'

ecfg['maintenance_permanent_logs'] = 'on'
ecfg['source_deinterlacing'] = 'on'

