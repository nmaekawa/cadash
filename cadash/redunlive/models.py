# -*- coding: utf-8 -*-
"""models for redunlive module."""
import arrow
import logging
import requests

from cadash.redunlive import utils


class CaptureAgent(object):
    """
    object to proxy a epiphan-pearl device livestream status.

    the device is the source of truth, and when unreachable, the proxy status
    is 'not available'
    """
    def __init__(self, serial_number, address):
        self._serial_number = serial_number
        self._address = address

        (name, trash) = self.address.split('.', 1)
        self._name = self.clean_name(name)

        self.client = None
        self._last_update = arrow.get(2000, 1, 1)

        # for now, the livestream channel# must be set externally
        self.channels = {
                'live': {
                    'channel': 'not available',
                    'publish_type': 'not available'},
                'lowBR': {
                    'channel': 'not available',
                    'publish_type': 'not available'},
            }


    @staticmethod
    def clean_name(name):
        return utils.clean_name(name)


    @property
    def serial_number(self):
        return self._serial_number


    @property
    def address(self):
        return self._address


    @property
    def last_update(self):
        return self._last_update


    @property
    def name(self):
        return self._name


    def __get_channel_publish_type(self, chan_name):
        chan = self.channels[chan_name]

        logger = logging.getLogger(__name__)
        logger.debug(
                'device(%s) channel(%s) is (%s)' %
                (self.name, chan_name, chan['channel']))

        if chan['channel'] == 'not available' or self.client is None:
            return 'not available'

        try:
            response = self.client.get_params(
                    channel=chan['channel'], params={'publish_type': ''})
            self._last_update = arrow.utcnow()

            logger.debug(
                    'device(%s) channel(%s)=(%s) publish_type=(%s)' %
                    (self.name, chan_name, chan['channel'], response))

        except requests.HTTPError as e:
            logger.warning(
                    'CA(%s) unable to get channel(%s) publish_type. error: %s' %
                    (self.name, chan_name, e.message))

            return 'not available'
        else:
            return response['publish_type'] \
                    if 'publish_type' in response else 'not available'


    def __set_channel_publish_type(self, chan_name, value):
        chan = self.channels[chan_name]
        if chan['channel'] == 'not available' or self.client is None:
            return 'not available'

        logger = logging.getLogger(__name__)
        try:
            self.client.set_params(
                    channel=self.channels[chan_name]['channel'],
                    params={'publish_type': value})
            self._last_update = arrow.utcnow()
        except requests.HTTPError as e:
            logger.warning(
                    'CA(%s) unable to set channel(%s) publish_type to %s. error: %s'
                    % (self.name, chan_name, value, e.message))
            return 'not available'

        else:
            logger.warning(
                    'CA(%s) channel(%s) publish_type set to %s'
                    % (self.name, chan_name, value))
            return value


    def sync_live_status(self):
        """
        refresh status of local object with info from capture agent.

        read publish_type from capture agent, both 'live' and 'lowBR' channels,
        and refresh status of local object
        if channels have diverging live status, try to set 'lowBR' publish_type
        as the same as 'live'
        """
        logger = logging.getLogger(__name__)
        logger.debug('in sync_live_status for device(%s)' % self.name)
        live = self.__get_channel_publish_type('live')
        lowBR = self.__get_channel_publish_type('lowBR')

        if live == lowBR:
            self.channels['live']['publish_type'] = live
            self.channels['lowBR']['publish_type'] = lowBR
        else:
            logger.warning(
                    'CA(%s) publish_type for live/lowBR (%s/%s); trying to fix...'
                    % (self.name, live, lowBR))
            value = self.__set_channel_publish_type('lowBR', live)

            if value == live:
                logger.warning(
                        'CA(%s) publish_type for live/lowBR fixed (%s)'
                        % (self.name, value))
            else:
                logger.warning(
                        'CA(%s) unable to fix publish_type for lowBR to (%s)'
                        % (self.name, live))

            # finally set channels to whatever was possible to set
            self.channels['live']['publish_type'] = live
            self.channels['lowBR']['publish_type'] = value


    def write_live_status(self, publish_type):
        """set capture agent live status for both 'live' and 'lowBR' channels."""
        self.channels['live']['publish_type'] = \
            self.__set_channel_publish_type('live', publish_type)
        self.channels['lowBR']['publish_type'] = \
            self.__set_channel_publish_type('lowBR', publish_type)

        # not ideal, but check that live and lowBR have the correct publish_type
        # is left to the user...
        return publish_type


    def __repr__(self):
        return u'%s_%s' % (self._name, self._serial_number)


    # for debug purposes!
    def debug_print(self):
        return """CaptureAgent: %s
        serial_number: %s
        address:       %s
        live_channel:  %s
        live_status:   %s
        lowBR_channel: %s
        lowBR_status:  %s
        last_update:   %s
        """ % (self._name,
               self._serial_number,
               self._address,
               self.channels['live']['channel'],
               self.channels['live']['publish_type'],
               self.channels['lowBR']['channel'],
               self.channels['lowBR']['publish_type'],
               self._last_update.to('local').format('YYYY-MM-DD HH:mm:ss ZZ'))



class CaLocation(object):

    def __init__(self, name):
        self._id = self.clean_name(name)
        self._primary_ca = None
        self._secondary_ca = None

        self.name = name
        self.experimental_cas = []


    @staticmethod
    def clean_name(name):
        return utils.clean_name(name)


    @property
    def id(self):
        return self._id


    @property
    def primary_ca(self):
        return self._primary_ca

    @primary_ca.setter
    def primary_ca(self, primary):
        if not isinstance(primary, CaptureAgent):
            raise TypeError('arg "primary" must be of type "CaptureAgent"')

        self._primary_ca = primary
        if self._secondary_ca and self._secondary_ca.serial_number == primary.serial_number:
            raise ValueError('same capture agent for primary and secondary not allowed')


    @property
    def secondary_ca(self):
        return self._secondary_ca

    @secondary_ca.setter
    def secondary_ca(self, secondary):
        if not isinstance(secondary, CaptureAgent):
            raise TypeError('arg "secondary" must be of type "CaptureAgent"')

        self._secondary_ca = secondary
        if self._primary_ca and self._primary_ca.serial_number == secondary.serial_number:
            raise ValueError('same capture agent for secondary AND primary not allowed')


    @property
    def active_livestream(self):
        if self._primary_ca is not None:
            if self._primary_ca.channels['live']['publish_type'] == '6':
                return 'primary'

        if self._secondary_ca is not None:
            if self._secondary_ca.channels['live']['publish_type'] == '6':
                return 'secondary'

        # there's no active livestream
        return None


    def __repr__(self):
        return self._id


    # for debug purposes
    def debug_print(self):
        s = """Location: %s
        active_livestream: %s
        """ % (self._id,
               self.active_livestream)

        s += """primary_ca: %s
        secondary_ca: %s
        experimental_ca: [
        """ % (self.primary_ca.debug_print(), self.secondary_ca.debug_print())

        for c in self.experimental_cas:
            s += c.debug_print()
        s += ']'
        return s
