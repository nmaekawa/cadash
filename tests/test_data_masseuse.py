# -*- coding: utf-8 -*-
"""Tests for `data_masseuse` module."""
import os
import pytest

import json
import httpretty

from cadash.redunlive.models import CaLocation
from cadash.redunlive.data_masseuse import map_redunlive_ca_loc

data_filename = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 'ca_loc_shortmap.json')

@pytest.mark.usefixtures('testapp')
class TestDataMasseuse(object):

    def setup(self):
        txt = open(data_filename, 'r')
        self.raw_data = txt.read()
        self.json_data = json.loads(self.raw_data)
        txt.close()


    @httpretty.activate
    def test_redunlive_ok_data(self):

        httpretty.register_uri(
                httpretty.GET,
                'http://fake-epiphan033.dce.harvard.edu/admin/channel3/get_params.cgi',
                body='publish_type = 0')
        httpretty.register_uri(
                httpretty.GET,
                'http://fake-epiphan033.dce.harvard.edu/admin/channel4/get_params.cgi',
                body='publish_type = 6')
        httpretty.register_uri(
                httpretty.GET,
                'http://fake-epiphan033.dce.harvard.edu/admin/channel4/set_params.cgi',
                body='', status=201)
        httpretty.register_uri(
                httpretty.GET,
                'http://fake-epiphan017.dce.harvard.edu/admin/channel3/get_params.cgi',
                body='publish_type = 6')
        httpretty.register_uri(
                httpretty.GET,
                'http://fake-epiphan017.dce.harvard.edu/admin/channel4/get_params.cgi',
                body='publish_type = 6')
        httpretty.register_uri(
                httpretty.GET,
                'http://fake-epiphan089.dce.harvard.edu/admin/channel3/get_params.cgi',
                body='publish_type = 0')
        httpretty.register_uri(
                httpretty.GET,
                'http://fake-epiphan089.dce.harvard.edu/admin/channel4/get_params.cgi',
                body='publish_type = 0')
        httpretty.register_uri(
                httpretty.GET,
                'http://fake-epiphan088.dce.harvard.edu/admin/channel3/get_params.cgi',
                body='publish_type = 0')
        httpretty.register_uri(
                httpretty.GET,
                'http://fake-epiphan088.dce.harvard.edu/admin/channel4/get_params.cgi',
                body='publish_type = 0')

        result = map_redunlive_ca_loc(self.json_data)

        assert isinstance(result, dict)
        assert 'all_locations' in result.keys()
        assert 'all_cas' in result.keys()
        assert len(result['all_locations']) == 1
        assert len(result['all_cas']) == 4

        assert isinstance(result['all_locations'], dict)
        assert 'fake_room' in result['all_locations'].keys()

        loc = result['all_locations']['fake_room']
        assert isinstance(loc, CaLocation)
        assert len(loc.experimental_cas) == 2

        assert loc.primary_ca is not None
        assert loc.primary_ca.channels['live']['publish_type'] == '0'
        assert loc.active_livestream == 'secondary'
