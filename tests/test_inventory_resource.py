# -*- coding: utf-8 -*-
"""tests inventory rest resources.

See: http://webtest.readthedocs.org/
"""
import os

import httpretty
import json
import pytest

from flask import url_for
from mock import patch

from cadash import utils
from cadash.inventory.dce_models import DceConfigForEpiphanCa
from cadash.inventory.dce_models import DceConfigForEpiphanCaFactory
from cadash.inventory.models import AkamaiStreamingConfig
from cadash.inventory.models import Ca
from cadash.inventory.models import EpiphanRecorder
from cadash.inventory.models import Location
from cadash.inventory.models import MhCluster
from cadash.inventory.models import Role
from cadash.inventory.models import Vendor


@pytest.mark.usefixtures('db', 'simple_db', 'testapp')
class TestCaResourceAuthenticated(object):
    def test_should_fail_when_not_auth(simple_db, testapp):
        res = testapp.get('/api/inventory/cas', expect_errors=True)
        assert res.status_int == 401


@pytest.mark.usefixtures('db', 'simple_db', 'testapp_login_disabled')
class TestCaResource(object):
    """capture agent rest resource."""

    def test_can_get_ca_list(self, testapp_login_disabled, simple_db):
        """get list of capture agents."""
        res = testapp_login_disabled.get('/api/inventory/cas')
        assert isinstance(res.body, str)
        json_data = json.loads(res.body)
        assert len(json_data) == 5
        assert json_data[3]['name'] == simple_db['ca'][3].name
        assert json_data[3]['serial_number'] == simple_db['ca'][3].serial_number


    def test_get_ca(self, testapp_login_disabled, simple_db):
        """get capture agent by id."""
        url = '/api/inventory/cas/%i' % simple_db['ca'][1].id
        res = testapp_login_disabled.get(url)
        json_data = json.loads(res.body)
        assert isinstance(json_data, dict)
        assert json_data['name'] == simple_db['ca'][1].name
        assert json_data['vendor_name_id'] == simple_db['vendor'].name_id


    def test_create_ca(self, testapp_login_disabled, simple_db):
        """create new capture agent - happy path."""
        new_ca = dict(name='fake-ca', address='fake-ca.some.url',
                vendor_id=simple_db['vendor'].id, serial_number='ABC123')
        res = testapp_login_disabled.post_json('/api/inventory/cas', new_ca)
        assert res.status_int == 201

        ca_list = Ca.query.all()
        assert len(ca_list) == 6

        json_ca = json.loads(res.body)
        assert bool(json_ca['id'])

        ca = Ca.get_by_id(json_ca['id'])
        assert ca.name == new_ca['name']
        assert ca.serial_number == new_ca['serial_number']
        assert ca.vendor_id == new_ca['vendor_id']


    def test_should_fail_to_create_ca_when_vendor_not_found(
            self, testapp_login_disabled):
        """vendor not found."""
        new_ca = dict(name='fake-ca', address='fake-ca.some.url',
                vendor_id=999999, serial_number='ABC123')
        res = testapp_login_disabled.post_json(
                '/api/inventory/cas', params=new_ca, expect_errors=True)
        assert res.status_int == 400
        error_msg = 'not in inventory: vendor_id(%i)' % new_ca['vendor_id']
        assert error_msg in res.body


    def test_should_fail_to_create_duplicate_name_ca(
            self, testapp_login_disabled, simple_db):
        new_ca = dict(name=simple_db['ca'][0].name, address='fake-ca.some.url',
                vendor_id=simple_db['vendor'].id, serial_number='ABC123')
        res = testapp_login_disabled.post_json(
                '/api/inventory/cas', params=new_ca, expect_errors=True)
        assert res.status_int == 400
        error_msg = 'duplicate ca name(%s)' % new_ca['name']
        assert error_msg in res.body


    def test_should_fail_to_create_duplicate_ca_address(
            self, testapp_login_disabled, simple_db):
        new_ca = dict(name='fake-ca', address=simple_db['ca'][0].address,
                vendor_id=simple_db['vendor'].id, serial_number='ABC123')
        res = testapp_login_disabled.post_json(
                '/api/inventory/cas', params=new_ca, expect_errors=True)
        assert res.status_int == 400
        error_msg = 'duplicate ca address(%s)' % new_ca['address']
        assert error_msg in res.body


    def test_should_fail_to_create_duplicate_ca_serial_number(
            self, testapp_login_disabled, simple_db):
        new_ca = dict(name='fake-ca', address='fake-ca.some.url',
                vendor_id=simple_db['vendor'].id,
                serial_number=simple_db['ca'][1].serial_number)
        res = testapp_login_disabled.post_json(
                '/api/inventory/cas', params=new_ca, expect_errors=True)
        assert res.status_int == 400
        error_msg = 'duplicate ca serial_number(%s)' % new_ca['serial_number']
        assert error_msg in res.body


    def test_should_fail_to_update_duplicate_name_ca(
            self, testapp_login_disabled, simple_db):
        ca = dict(name=simple_db['ca'][0].name, address='fake-ca.some.url',
                vendor_id=simple_db['vendor'].id, serial_number='ABC123')
        res = testapp_login_disabled.put_json(
                '/api/inventory/cas/%i' % simple_db['ca'][1].id,
                params=ca, expect_errors=True)
        assert res.status_int == 400
        error_msg = 'duplicate ca name(%s)' % ca['name']
        assert error_msg in res.body


    def test_update_name_ca(
            self, testapp_login_disabled, simple_db):
        ca = dict(name='fake-name')
        res = testapp_login_disabled.put_json(
                '/api/inventory/cas/%i' % simple_db['ca'][1].id, params=ca)
        assert res.status_int == 200
        ca_updated = Ca.get_by_id(simple_db['ca'][1].id)
        assert ca_updated.name == ca['name']


@pytest.mark.usefixtures('db', 'simple_db', 'testapp_login_disabled')
class TestLocationResource(object):
    """location rest resource."""

    def test_can_get_location_list(self, testapp_login_disabled, simple_db):
        """get list of location."""
        res = testapp_login_disabled.get('/api/inventory/locations')
        assert bool(res)
        json_data = json.loads(res.body)
        assert len(json_data) == 5
        assert json_data[3]['name'] == simple_db['room'][3].name

    def test_get_lecation(self, testapp_login_disabled, simple_db):
        """get location by id."""
        url = '/api/inventory/locations/%i' % simple_db['room'][1].id
        res = testapp_login_disabled.get(url)
        json_data = json.loads(res.body)
        assert isinstance(json_data, dict)
        assert json_data['name'] == simple_db['room'][1].name
        assert json_data['primary_pr_vconnector'] == 'sdi'
        assert json_data['primary_pr_vinput'] == 'a'

    def test_create_location(self, testapp_login_disabled, simple_db):
        """create new location - happy path."""
        l = dict(name='fake-ROOM')
        res = testapp_login_disabled.post_json('/api/inventory/locations', l)
        assert res.status_int == 201

        l_list = Location.query.all()
        assert len(l_list) == 6

        json_data = json.loads(res.body)
        assert bool(json_data['id'])

        loc = Location.get_by_id(json_data['id'])
        assert loc.name == l['name']


    def test_should_fail_when_create_duplicate_name(
            self, testapp_login_disabled, simple_db):
        """name is unique."""
        l = dict(name=simple_db['room'][0].name)
        res = testapp_login_disabled.post_json('/api/inventory/locations',
                params=l, expect_errors=True)
        json_data = json.loads(res.body)
        assert res.status_int == 400
        error_msg = 'duplicate location name(%s)' % simple_db['room'][0].name
        assert error_msg in res.body


    def test_should_fail_when_create_missing_name(
            self, testapp_login_disabled, simple_db):
        """name is unique."""
        l = dict(fake_arg='fake_value')
        res = testapp_login_disabled.post_json('/api/inventory/locations',
                params=l, expect_errors=True)
        json_data = json.loads(res.body)
        assert res.status_int == 400
        assert '`name` cannot be blank' in res.body


    def test_update(self, testapp_login_disabled, simple_db):
        """update happy path."""
        loc = Location.get_by_id(simple_db['room'][2].id)
        assert loc.name == simple_db['room'][2].name

        l = dict(
                name='special_new_name',
                primary_pr_vconnector='hdmi',
                primary_pr_vinput='k',
                )
        url = '/api/inventory/locations/%i' % simple_db['room'][2].id
        res = testapp_login_disabled.put_json(url, params=l)

        loc = Location.get_by_id(simple_db['room'][2].id)
        assert loc.name == 'special_new_name'
        assert loc.config.primary_pr_vconnector == 'hdmi'
        assert loc.config.primary_pr_vinput == 'k'


    def test_should_fail_when_update_blank_name(
            self, testapp_login_disabled, simple_db):
        """name is unique."""
        l = dict(name='   ')
        url = '/api/inventory/locations/%i' % simple_db['room'][2].id
        res = testapp_login_disabled.put_json(url, params=l, expect_errors=True)
        assert res.status_int == 400
        assert 'not allowed empty value for `name`' in res.body


@pytest.mark.usefixtures('db', 'simple_db', 'testapp_login_disabled')
class TestVendorResource(object):
    """vendor rest resource."""

    def test_can_get_vendor_list(self, testapp_login_disabled, simple_db):
        """get list of vendor."""
        res = testapp_login_disabled.get('/api/inventory/vendors')
        assert bool(res)
        json_data = json.loads(res.body)
        assert len(json_data) == 1
        assert json_data[0]['name_id'] == simple_db['vendor'].name_id

    def test_get_vendor(self, testapp_login_disabled, simple_db):
        """get vendor by id."""
        url = '/api/inventory/vendors/%i' % simple_db['vendor'].id
        res = testapp_login_disabled.get(url)
        json_data = json.loads(res.body)
        assert isinstance(json_data, dict)
        assert json_data['name_id'] == simple_db['vendor'].name_id
        assert json_data['datetime_ntpserver'] == '0.pool.ntp.org'
        assert json_data['touchscreen_allow_recording'] == False
        assert json_data['touchscreen_timeout_secs'] == 600

    def test_create_vendor(self, testapp_login_disabled, simple_db):
        """create new vendor - happy path."""
        v = dict(name='calling', model='i.c.wiener')
        res = testapp_login_disabled.post_json('/api/inventory/vendors', v)
        assert res.status_int == 201

        v_list = Vendor.query.all()
        assert len(v_list) == 2

        json_data = json.loads(res.body)
        assert bool(json_data['id'])

        vendor = Vendor.get_by_id(json_data['id'])
        assert vendor.name == v['name']
        assert vendor.config.datetime_ntpserver == '0.pool.ntp.org'
        assert vendor.config.touchscreen_allow_recording == False
        assert vendor.config.touchscreen_timeout_secs == 600


    def test_should_fail_when_create_duplicate_name(
            self, testapp_login_disabled, simple_db):
        """name is unique."""
        l = dict(name=simple_db['vendor'].name, model=simple_db['vendor'].model)
        res = testapp_login_disabled.post_json('/api/inventory/vendors',
                params=l, expect_errors=True)
        json_data = json.loads(res.body)
        assert res.status_int == 400
        error_msg = 'duplicate vendor name_model(%s)' \
                % simple_db['vendor'].name_id
        assert error_msg in res.body


    def test_update(self, testapp_login_disabled, simple_db):
        """update happy path."""
        vendor = Vendor.get_by_id(simple_db['vendor'].id)
        assert vendor.name_id == simple_db['vendor'].name_id

        v = dict(
                model='tralala',
                datetime_ntpserver='ntp.harvard.edu',
                source_deinterlacing=False,
                touchscreen_timeout_secs=123)
        url = '/api/inventory/vendors/%i' % simple_db['vendor'].id
        res = testapp_login_disabled.put_json(url, params=v)

        vendor = Vendor.get_by_id(simple_db['vendor'].id)
        assert vendor.name_id == Vendor.computed_name_id(
                name=simple_db['vendor'].name, model='tralala')
        assert vendor.config.datetime_ntpserver == 'ntp.harvard.edu'
        assert vendor.config.source_deinterlacing == False
        assert vendor.config.touchscreen_timeout_secs == 123


    def test_update_blank_name(
            self, testapp_login_disabled, simple_db):
        """name is unique."""
        v = dict(name='   ',)
        model = utils.clean_name(simple_db['vendor'].model)
        url = '/api/inventory/vendors/%i' % simple_db['vendor'].id
        res = testapp_login_disabled.put_json(url, params=v)
        assert res.status_int == 200

        json_data = json.loads(res.body)
        assert json_data['id'] == simple_db['vendor'].id
        assert json_data['name_id'] == '_%s' % model


@pytest.mark.usefixtures('db', 'simple_db', 'testapp_login_disabled')
class TestMhClusterResource(object):
    """mh_cluster rest resource."""

    def test_can_get_cluster_list(self, testapp_login_disabled, simple_db):
        """get list of cluster."""
        res = testapp_login_disabled.get('/api/inventory/clusters')
        assert bool(res)
        json_data = json.loads(res.body)
        assert len(json_data) == 3
        assert json_data[0]['name'] == simple_db['cluster'][0].name

    def test_get_cluster(self, testapp_login_disabled, simple_db):
        """get cluster by id."""
        url = '/api/inventory/clusters/%i' % simple_db['cluster'][0].id
        res = testapp_login_disabled.get(url)
        json_data = json.loads(res.body)
        assert isinstance(json_data, dict)
        assert json_data['name'] == simple_db['cluster'][0].name

    def test_create_cluster(self, testapp_login_disabled, simple_db):
        """create new vendor - happy path."""
        c = dict(name='gojira', admin_host='http://some.url.net', env='prod')
        res = testapp_login_disabled.post_json('/api/inventory/clusters', c)
        assert res.status_int == 201

        c_list = MhCluster.query.all()
        assert len(c_list) == 4

        json_data = json.loads(res.body)
        assert bool(json_data['id'])

        cluster = MhCluster.get_by_id(json_data['id'])
        assert cluster.name == c['name']


    def test_should_fail_when_create_duplicate_name(
            self, testapp_login_disabled, simple_db):
        """name is unique."""
        c = dict(name=simple_db['cluster'][0].name,
                admin_host='http://doh.doh.doh', env='stage')
        res = testapp_login_disabled.post_json('/api/inventory/clusters',
                params=c, expect_errors=True)
        json_data = json.loads(res.body)
        assert res.status_int == 400
        error_msg = 'duplicate mh_cluster name(%s)' \
                % simple_db['cluster'][0].name
        assert error_msg in res.body


    def test_update(self, testapp_login_disabled, simple_db):
        """update happy path."""
        cluster = MhCluster.get_by_id(simple_db['cluster'][1].id)
        assert cluster.name == simple_db['cluster'][1].name

        c = dict(env='StAgE')
        url = '/api/inventory/clusters/%i' % simple_db['cluster'][1].id
        res = testapp_login_disabled.put_json(url, params=c)

        cluster = MhCluster.get_by_id(simple_db['cluster'][1].id)
        assert cluster.env == 'stage'


    def test_update_invalid_mh_env(
            self, testapp_login_disabled, simple_db):
        """env is restricted to values prod|dev|stage."""
        c = dict(env='mothra',)
        url = '/api/inventory/clusters/%i' % simple_db['cluster'][2].id
        res = testapp_login_disabled.put_json(url, params=c, expect_errors=True)
        assert res.status_int == 400
        assert 'mh cluster env value not in' in res.body


@pytest.mark.usefixtures('db', 'simple_db', 'testapp_login_disabled')
class TestRoleResource(object):
    """role rest resource."""

    def test_can_get_role_list(self, testapp_login_disabled, simple_db):
        """get list of roles."""
        res = testapp_login_disabled.get('/api/inventory/roles')
        assert bool(res)
        json_data = json.loads(res.body)
        assert isinstance(json_data, list)
        assert len(json_data) == 3
        assert json_data[0]['ca_id'] == simple_db['ca'][0].id

    def test_get_role(self, testapp_login_disabled, simple_db):
        """get single role, by ca.id."""
        res = testapp_login_disabled.get('/api/inventory/roles/%i' %
                simple_db['ca'][2].id)
        json_data = json.loads(res.body)
        assert json_data['ca_id'] == simple_db['ca'][2].id
        assert json_data['name'] == simple_db['ca'][2].role.name

    def test_should_fail_in_update(self, testapp_login_disabled, simple_db):
        """update not allowed for roles."""
        res = testapp_login_disabled.put('/api/inventory/roles/%i' %
                simple_db['ca'][0].id, expect_errors=True)
        assert res.status_int == 405
        assert 'not allowed to update' in res.body

    def test_delete(self, testapp_login_disabled, simple_db):
        """delete role."""
        res = testapp_login_disabled.delete('/api/inventory/roles/%i' %
                simple_db['ca'][2].id)
        assert res.status_int == 204
        assert simple_db['ca'][2].role is None


@pytest.mark.usefixtures('db', 'simple_db', 'testapp_login_disabled')
class TestStreamingConfigResource(object):
    """akamai_streaming_config rest resource."""

    def test_can_get_streamcfg_list(self, testapp_login_disabled, simple_db):
        """get list of streamcfg."""
        res = testapp_login_disabled.get('/api/inventory/streamcfgs')
        assert bool(res)
        json_data = json.loads(res.body)
        assert len(json_data) == 1
        assert json_data[0]['name'] == simple_db['stream_config'].name

    def test_get_streamcfg(self, testapp_login_disabled, simple_db):
        """get streamcfg by id."""
        url = '/api/inventory/streamcfgs/%i' % simple_db['stream_config'].id
        res = testapp_login_disabled.get(url)
        json_data = json.loads(res.body)
        assert isinstance(json_data, dict)
        assert json_data['name'] == simple_db['stream_config'].name

    def test_create_streamcfg(self, testapp_login_disabled, simple_db):
        """create new streamcfg - happy path."""
        c = dict(
                name='gojira', stream_id='333333',
                stream_user='jon', stream_password='snow')
        res = testapp_login_disabled.post_json('/api/inventory/streamcfgs', c)
        assert res.status_int == 201

        c_list = AkamaiStreamingConfig.query.all()
        assert len(c_list) == 2

        json_data = json.loads(res.body)
        assert bool(json_data['id'])

        stream_config = AkamaiStreamingConfig.get_by_id(json_data['id'])
        assert stream_config.name == c['name']


    def test_should_fail_when_create_duplicate_stream_id(
            self, testapp_login_disabled, simple_db):
        """stream_id is unique."""
        c = dict(name='different_name_for_stream',
                stream_id=simple_db['stream_config'].stream_id,
                stream_user='jon', stream_password='snow')
        res = testapp_login_disabled.post_json('/api/inventory/streamcfgs',
                params=c, expect_errors=True)
        json_data = json.loads(res.body)

        assert res.status_int == 400
        error_msg = 'duplicate stream_id({})'.format(
                simple_db['stream_config'].stream_id)
        assert error_msg in res.body


    def test_should_fail_when_update(self, testapp_login_disabled, simple_db):
        """update happy path."""
        url = '/api/inventory/streamcfgs/%i' % simple_db['stream_config'].id
        res = testapp_login_disabled.put_json(url, expect_errors=True)
        assert res.status_int == 405
        assert 'not allowed to update' in res.body


@pytest.mark.usefixtures('db', 'simple_db', 'testapp_login_disabled')
class TestCaConfigResource(object):
    """capture agent Config rest resource."""

    def test_get_cacfg(self, testapp_login_disabled, simple_db):
        """get ca config by ca_id."""
        ca = simple_db['ca'][2]
        ca_cfg = DceConfigForEpiphanCaFactory.retrieve(ca_id=ca.id)
        local_cfg = ca.role.config
        i = 10
        for rec in local_cfg.recorders:
            rec.update(recorder_id_in_device=i)
            i += 1
        for chan in local_cfg.channels:
            chan.update(channel_id_in_device=i)
            i += 1

        url = '/api/inventory/cas/{}/config'.format(ca.id)
        res = testapp_login_disabled.get(url)
        json_data = json.loads(res.body)
        assert isinstance(json_data, dict)
        assert json_data['role'] == ca_cfg.role_name
        assert json_data == ca_cfg.epiphan_dce_config


@pytest.mark.usefixtures('db', 'simple_db', 'testapp_login_disabled')
class TestEpiphanRecorderResource(object):
    """recorders configured for a capture agent."""

    def test_get_recorder(self, testapp_login_disabled, simple_db):
        ca = simple_db['ca'][0]
        recorders = ca.role.config.recorders

        url = '/api/inventory/cas/{}/recorders/{}'.format(
                ca.id, recorders[0].name)
        res = testapp_login_disabled.get(url)
        json_data = json.loads(res.body)
        assert isinstance(json_data, dict)
        for key in json_data:
            assert json_data[key] == recorders[0].__getattribute__(key)

    def test_update_recorder(self, testapp_login_disabled, simple_db):
        ca = simple_db['ca'][0]
        rec = ca.role.config.recorders[1]

        url = '/api/inventory/cas/{}/recorders/{}'.format(ca.id, rec.name)
        params = dict(recorder_id_in_device=6, output_format='mp4',
                time_limit_in_minutes=120)
        res = testapp_login_disabled.put_json(url, params=params)
        json_data = json.loads(res.body)
        assert isinstance(json_data, dict)
        assert json_data['recorder_id_in_device'] == 6
        assert json_data['output_format'] == 'mp4'
        assert json_data['time_limit_in_minutes'] == 120
        assert json_data['size_limit_in_kbytes'] == 64000000

    def test_get_recorder_list(self, testapp_login_disabled, simple_db):
        ca = simple_db['ca'][0]

        url = '/api/inventory/cas/{}/recorders/'.format(ca.id)
        res = testapp_login_disabled.get(url)
        json_data = json.loads(res.body)
        assert isinstance(json_data, list)
        assert len(json_data) == 2
        assert json_data[0]['name'] == 'recorder_fake'
        assert json_data[1]['name'] == 'recorder_fake_2'  # can guarantee order?

    def test_create_recorder(self, testapp_login_disabled, simple_db):
        ca = simple_db['ca'][0]

        url = '/api/inventory/cas/{}/recorders/'.format(ca.id)
        params = dict(name='brand_new_recorder')
        res = testapp_login_disabled.post_json(url, params=params)
        json_data = json.loads(res.body)
        assert isinstance(json_data, dict)
        assert json_data['name'] == 'brand_new_recorder'
        assert json_data['output_format'] == 'avi'
        assert json_data['recorder_id_in_device'] == 99999





