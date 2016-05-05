# -*- coding: utf-8 -*-
"""models for epiphan-pearl capture agent devices.

this approach considers that the device can take input via `connectors`, like
hdmi|sdi|vga|analog, and that connectors can take audio or video or both signals.
so, an audio signal via `connector` hdmi is called a `source`.

epiphan-pearls have 2 groups of inputs via a set of connectors, usually called
'A' and 'B'. So, for example, an audio SDI signal in group 'A'is named 'SDI-A Audio'.

from sources, you can create `channels` (that can combine multiple sources).

for automatically recording channels, create a `recorder`.
"""

import logging

from cadash.config.errors MalformedJsonError


class EpipearlSource(object):
    """model for epiphan sources."""

    def __init__(source):
        """create instance based on device source json."""
        if 'audio' in source and source['audio']:
            self._type = 'audio'
        if 'video' in source and source['video']:
            self._type = 'video'
        if 'name' in source:
            self._name = source['name']
        if 'id' in source:
            self._sid = source['id']
            self._did, sname = source['id'].split('.', 1)
            nlist = sname.split('-', 2)
            if len(nlist) > 1:
                self._connector = nlist[0]
                self._group = nlist[1]

        if not self._type:
            raise MalformedJsonError('source json missing "type"(as in audio|video)')
        elif not self._name:
            raise MalformedJsonError('source json missing "name"')
        elif not self_sid:
            raise MalformedJsonError('source json missing "id"')
        elif not self._did:
            raise MalformedJsonError('source json missing "id"(as in device id)')
        elif not self._connector:
            raise MalformedJsonError('source json missing "id"(as in source connector)')
        elif not self._group:
            raise MalformedJsonError('source json missing "id"(as in device group)')

    @property
    def group(self):
        return self._group

    @property
    def is_audio(self):
        return self._type == 'audio'

    @property
    def source_id(self):
        return self._sid

    @property
    def connector(self):
        return self._connector

    @property
    def name(self):
        return self._name

    @property
    def device_id(self):
        return self._did


class EpipearlSources(object):
    """epiphan source list."""

    def __init__(self, sources):
        """ create instance based on device source json.

        `sources` is a list (converted from json), as returned in
            response = http://<epiphan>/ajax/devices.cgi
            response.json()['result']
        """
        self._sources = {}
        self._source_map = {}
        for source in sources:
            try:
                s = EpipearlSource(source)
            except MalformedJsonError as e:
                logger = logging.getLogger(__name__)
                msg = 'cannot parse input source info; '
                msg += 'error(%s); ' % e.message
                msg += 'source_original<%s>' % json.dumps(s)
                logger.error(msg)
                ### todo: can go on without all correct sources?

            if s.group not in self._sources:
                self._sources[s.group] = {}
            if s.connector not in self._sources[s.group]:
                self._sources[s.group][s.connector] = {}
            if s.is_audio:
                self._sources[s.group][s.connector]['audio'] = s
            else:
                self._sources[s.group][s.connector]['video'] = s
            self._source_map[s.name] = s

    def sources_as_map(self):
        return self._source_map

    def sources_per_group(self):
        return self._sources


class EpipearlChannel(object):
    """model for epiphan channels."""

    id
    name
    sources
    configs

    def __init__(self, channel_id, name):
        """create instance."""

"""
just created channel in configdb
::vgabroadcasterlite7:::
    ::vgabroadcasterlite7:FRAMESIZE::1920x1080
    ::vgabroadcasterlite7:CODEC::h.264
    ::vgabroadcasterlite7:VBITRATE::
    ::vgabroadcasterlite7:VBUFMODE::0
    ::vgabroadcasterlite7:FPSLIMIT::30
    ::vgabroadcasterlite7:VKEYFRAMEINTERVAL::1
    ::vgabroadcasterlite7:VENCPRESET::5
    ::vgabroadcasterlite7:VPROFILE::100
    ::vgabroadcasterlite7:FRAMESIZE_FROM_SIGNAL::on
    ::vgabroadcasterlite7:STREAMPORT::8006
    ::vgabroadcasterlite7:RTSP_PORT::560
    ::vgabroadcasterlite7:AUDIO::on
    ::vgabroadcasterlite7:AUDIOPRESET::libfaac;44100
    ::vgabroadcasterlite7:AUDIOBITRATE::320
    ::vgabroadcasterlite7:AUDIOCHANNELS::2
    ::vgabroadcasterlite7:LAYOUT_ORDER::1
    ::vgabroadcasterlite7:ACTIVE_LAYOUT::1
    ::vgabroadcasterlite7/layouts:::
    ::vgabroadcasterlite7/layouts/1:::
    ::vgabroadcasterlite7/layouts/1:NAME::Default
    ::vgabroadcasterlite7/layouts/1:SETTINGS::{"video":[],"audio":[],"background":"#000000"}

just created channel from /ajax/sysinfo.cgi
    {
      "id": "7",
      "codecs": {
        "audio": {
          "name": "AAC",
          "bitrate": "320"
        },
        "video": {
          "name": "H264",
          "bitrate": "6467000",
          "framesize": "1920x1080",
          "fps": "30.0"
        }
      },
      "uuid": "514b1522-6241-4457-8a9f-adbe229cba52",
      "state": "OK",
      "name": "Channel 7",
      "recorder": {
        "enabled": false,
        "state": "",
        "time": 0
      }
    }

after saving streaming
::vgabroadcasterlite7:::
::vgabroadcasterlite7:FRAMESIZE::1920x1080
::vgabroadcasterlite7:CODEC::h.264
::vgabroadcasterlite7:VBITRATE::
::vgabroadcasterlite7:VBUFMODE::0
::vgabroadcasterlite7:FPSLIMIT::30
::vgabroadcasterlite7:VKEYFRAMEINTERVAL::1
::vgabroadcasterlite7:VENCPRESET::5
::vgabroadcasterlite7:VPROFILE::100
::vgabroadcasterlite7:FRAMESIZE_FROM_SIGNAL::on
::vgabroadcasterlite7:STREAMPORT::8006
::vgabroadcasterlite7:RTSP_PORT::560
::vgabroadcasterlite7:AUDIO::on
::vgabroadcasterlite7:AUDIOPRESET::libfaac;44100
::vgabroadcasterlite7:AUDIOBITRATE::320
::vgabroadcasterlite7:AUDIOCHANNELS::2
::vgabroadcasterlite7:LAYOUT_ORDER::1
::vgabroadcasterlite7:ACTIVE_LAYOUT::1
::vgabroadcasterlite7:BCAST_DISABLED::on
::vgabroadcasterlite7:HTTPLIVESTREAMING::
::vgabroadcasterlite7:UPNP_ENABLED::
::vgabroadcasterlite7:PUBLISH_TYPE::0
::vgabroadcasterlite7:PIP_LAYOUT::
::vgabroadcasterlite7:DVICHANNEL_ENABLED::
::vgabroadcasterlite7:UNICAST_ADDRESS::
::vgabroadcasterlite7:UNICAST_APORT::
::vgabroadcasterlite7:UNICAST_VPORT::
::vgabroadcasterlite7:UNICAST_MPORT::
::vgabroadcasterlite7:SAP::
::vgabroadcasterlite7:SAP_IP::
::vgabroadcasterlite7:SAP_CHANNEL_NO::
::vgabroadcasterlite7:SAP_PLAY_GROUP::
::vgabroadcasterlite7/layouts:::
::vgabroadcasterlite7/layouts/1:::
::vgabroadcasterlite7/layouts/1:NAME::Default
::vgabroadcasterlite7/layouts/1:SETTINGS::{"video":[],"audio":[],"background":"#000000"}
::vgabroadcasterlite7/publish:::
::vgabroadcasterlite7/publish/0:::
::vgabroadcasterlite7/publish/0:RTSP_URL::
::vgabroadcasterlite7/publish/0:RTSP_TRANSPORT::udp
::vgabroadcasterlite7/publish/0:RTSP_USERNAME::
::vgabroadcasterlite7/publish/0:RTSP_PASSWORD::
::vgabroadcasterlite7/publish/0:RTMP_URL::
::vgabroadcasterlite7/publish/0:RTMP_STREAM::
::vgabroadcasterlite7/publish/0:RTMP_USERNAME::
::vgabroadcasterlite7/publish/0:RTMP_PASSWORD::
::vgabroadcasterlite7/publish/0:LIVESTREAM_CHANNEL::
::vgabroadcasterlite7/publish/0:LIVESTREAM_USERNAME::
::vgabroadcasterlite7/publish/0:LIVESTREAM_PASSWORD::
"""



