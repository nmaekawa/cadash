# -*- coding: utf-8 -*-
"""default settings for dce epiphan."""

class SettingsFactory(object):
    """factory for ca dce settings for epiphans."""

    _settings = {
        # expected in settings for ca
        'Ca':  {
            'source_device_id': 'value',
            'firmware_version': 'value',
            'mhpearl_version': 'value',
            'pr': {
                'channel_id': '1',
                'layout': """{
                    "video":[
                    {
                        "type":"source",
                        "position": {
                            "left":"0%",
                            "top":"0%",
                            "width":"100%",
                            "height":"100%",
                            "keep_aspect_ratio":true
                        },
                        "settings": {
                            "source":"{{source_id}}.sdi-a"
                        }
                    }],
                    "audio":[
                    {
                        "type":"source",
                        "settings":
                            {"source":"{{source_id}}.sdi-a-audio"}
                    }],
                    "background":"#000000",
                    "nosignal":{
                        "id":"default"
                    }
                }""",
            },
            'pn': {
                'channel_id': '2',
                'layout': """{
                    "video":[
                    {
                        "type":"source",
                        "position":{
                            "left":"0%",
                            "top":"0%",
                            "width":"100%",
                            "height":"100%",
                            "keep_aspect_ratio":true
                        },
                        "settings":{
                            "source":"{{source_id}}.sdi-b"}
                    }],
                    "audio":[
                    {
                        "type":"source",
                        "settings":{
                            "source":"{{source_id}}.analog-b"
                        }
                    }],
                    "background":"#000000",
                    "nosignal":{
                        "id":"default"
                    }
                }""",
            },
            'live': {
                'channel_id': '3',
                'layout': """{
                    "video":[
                    {
                        "type":"source",
                        "position":{
                            "left":"0%",
                            "right":"50%",
                            "top":"0%",
                            "bottom":"0%",
                            "keep_aspect_ratio":true
                        },
                        "crop":{},
                        "settings":{
                            "source":"{{source_id}}.sdi-a"
                        }
                    },
                    {
                        "type":"source",
                        "position":{
                            "left":"50%",
                            "right":"0%",
                            "top":"0%",
                            "bottom":"0%",
                            "keep_aspect_ratio":true
                        },
                        "crop":{},
                        "settings":{
                            "source":"{{source_id}}.sdi-b"
                        }
                    }],
                    "audio":[
                    {
                        "type":"source",
                        "settings":{
                            "source":"{{source_id}}.sdi-a-audio"
                        }
                    } ],
                    "background":"#000000"
                }""",
            },
            'lowbr': {
                'channel_id': '4',
                'layout': """{
                    "video":[
                    {
                        "type":"source",
                        "position":{
                            "left":"0%",
                            "right":"50%",
                            "top":"0%",
                            "bottom":"0%",
                            "keep_aspect_ratio":true
                        },
                        "crop":{},
                        "settings":{
                            "source":"{{source_id}}.sdi-a"
                        }
                    },
                    {
                        "type":"source",
                        "position":{
                            "left":"50%",
                            "right":"0%",
                            "top":"0%",
                            "bottom":"0%",
                            "keep_aspect_ratio":true
                        },
                        "crop":{},
                        "settings":{
                            "source":"{{source_id}}.sdi-b"
                        }
                    }],
                    "audio":[
                    {
                        "type":"source",
                        "settings":{
                            "source":"{{source_id}}.sdi-a-audio"
                        }
                    }],
                    "background":"#000000"
                }""",
            },
            'pnpr': {
                'channel_id': 'm1',
                'layout': None,
            },
        },

        # expected in settings for epiphan vendor
        'Vendor': {
            'ntp_server': {
                'address': '0.us.pool.ntp.org',
                'timezone': 'US/Eastern',
            },
            'remote_support': {
                'permanent_logs': 'on',
            },
            'mhpearl': {
                'filesearch_range': '60',
            },
        },

    }

    @classmethod
    def settings_for_ca(self):
        return self._settings['Ca'].copy()

    @classmethod
    def settings_for_vendor(self):
        return self._settings['Vendor'].copy()
