# -*- coding: utf-8 -*-
"""Tests for `models` in redunlive webapp."""
import httpretty
import pytest
from epipearl import Epipearl

from cadash.redunlive.models import CaptureAgent
from cadash.redunlive.models import CaLocation


epiphan_url = 'http://fake.example.edu'


class TestCaptureAgentModel(object):

    def setup(self):
        p = CaptureAgent('ABCD1111', 'fake1.example.edu')
        p.channels['live']['channel'] = '1'
        p.channels['live']['publish_type'] = '0'
        p.channels['lowBR']['channel'] = '2'
        p.channels['lowBR']['publish_type'] = '0'
        p.client = Epipearl(epiphan_url, 'user', 'passwd')
        self.ca = p


    @httpretty.activate
    def test_get_converging_live_status(self):
        live = self.ca.channels['live']
        lowBR = self.ca.channels['lowBR']
        assert live['publish_type'] == '0'

        httpretty.register_uri(
                httpretty.GET, '%s/admin/channel%s/get_params.cgi' %
                (epiphan_url, live['channel']), body='publish_type = 6')
        httpretty.register_uri(
                httpretty.GET, '%s/admin/channel%s/get_params.cgi' %
                (epiphan_url, lowBR['channel']), body='publish_type = 6')

        self.ca.sync_live_status()
        assert live['publish_type'] == lowBR['publish_type']
        assert live['publish_type'] == '6'


    @httpretty.activate
    def test_get_diverging_live_status(self):
        live = self.ca.channels['live']
        lowBR = self.ca.channels['lowBR']

        httpretty.register_uri(
                httpretty.GET, '%s/admin/channel%s/get_params.cgi' %
                (epiphan_url, live['channel']), body='publish_type = 0')
        httpretty.register_uri(
                httpretty.GET, '%s/admin/channel%s/get_params.cgi' %
                (epiphan_url, lowBR['channel']), body='publish_type = 6')
        httpretty.register_uri(
                httpretty.GET, '%s/admin/channel%s/set_params.cgi' %
                (epiphan_url, lowBR['channel']), body='', status=201)

        self.ca.sync_live_status()
        assert live['publish_type'] == lowBR['publish_type']
        assert live['publish_type'] == '0'


    @httpretty.activate
    def test_set_live_status(self):
        live = self.ca.channels['live']
        lowBR = self.ca.channels['lowBR']

        httpretty.register_uri(
                httpretty.GET, '%s/admin/channel%s/set_params.cgi' %
                (epiphan_url, live['channel']), body='', status=201)
        httpretty.register_uri(
                httpretty.GET, '%s/admin/channel%s/set_params.cgi' %
                (epiphan_url, lowBR['channel']), body='', status=201)

        new_publish_status = '6'
        self.ca.write_live_status(new_publish_status)
        assert live['publish_type'] == lowBR['publish_type']
        assert live['publish_type'] == new_publish_status





class TestCaLocationModel(object):

    def setup(self):
        p = CaptureAgent('ABCD1111', 'fake1.example.edu')
        p.channels['live']['channel'] = '1'
        p.channels['live']['publish_type'] = '0'
        p.channels['lowBR']['channel'] = '2'
        p.channels['lowBR']['publish_type'] = '0'
        self.primary = p

        s = CaptureAgent('ABCD2222', 'fake2.example.edu')
        s.channels['live']['channel'] = '7'
        s.channels['live']['publish_type'] = '0'
        s.channels['lowBR']['channel'] = '8'
        s.channels['lowBR']['publish_type'] = '0'
        self.secondary = s

        e1 = CaptureAgent('ABCD3333', 'fake3.example.edu')
        e1.channels['live']['channel'] = '3'
        e1.channels['live']['publish_type'] = '0'
        e1.channels['lowBR']['channel'] = '4'
        e1.channels['lowBR']['publish_type'] = '0'
        self.experimental1 = e1

        e2 = CaptureAgent('ABCD4444', 'fake4.example.edu')
        e2.channels['live']['channel'] = '3'
        e2.channels['live']['publish_type'] = '0'
        e2.channels['lowBR']['channel'] = '4'
        e2.channels['lowBR']['publish_type'] = '0'
        self.experimental2 = e2

        l = CaLocation('loc1')
        l.primary_ca = self.primary
        l.secondary_ca = self.secondary
        l.experimental_cas = [self.experimental1, self.experimental2]
        self.loc = l


    def test_simple_location(self):
        assert self.loc.primary_ca.name == 'fake1'
        assert self.loc.secondary_ca.name == 'fake2'
        assert len(self.loc.experimental_cas) == 2
        assert self.loc.active_livestream is None


    def test_same_ca_for_secondary(self):
        with pytest.raises(ValueError):
            self.loc.secondary_ca = self.primary


    def test_same_ca_for_primary(self):
        with pytest.raises(ValueError):
            self.loc.primary_ca = self.secondary


    def test_toggle_active_livestream(self):
        assert self.loc.active_livestream is None

        self.primary.channels['live']['publish_type'] = '6'
        assert self.loc.active_livestream == 'primary'

        self.primary.channels['live']['publish_type'] = '0'
        self.secondary.channels['live']['publish_type'] = '6'
        assert self.loc.active_livestream == 'secondary'
