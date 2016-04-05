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

from cadash.inventory.models import Ca


@pytest.mark.usefixtures('db', 'simple_db', 'testapp_login_disabled')
class TestCaResource(object):
    """capture agent rest resource."""

    def test_can_get_ca_list(self, testapp_login_disabled, simple_db):
        """get list of capture agents."""
        res = testapp_login_disabled.get('/inventory/api/cas')
        assert bool(res)
        json_data = json.loads(res.body)
        assert len(json_data) == 5
        assert json_data[3]['name'] == simple_db['ca'][3].name
        assert json_data[3]['serial_number'] == simple_db['ca'][3].serial_number


    def test_get_ca(self, testapp_login_disabled, simple_db):
        """get capture agent by id."""
        url = '/inventory/api/cas/%i' % simple_db['ca'][1].id
        res = testapp_login_disabled.get(url)
        json_data = json.loads(res.body)
        assert isinstance(json_data, dict)
        assert json_data['name'] == simple_db['ca'][1].name
        assert json_data['vendor_name_id'] == simple_db['vendor'].name_id


    def test_create_ca(self, testapp_login_disabled, simple_db):
        """create new capture agent - happy path."""
        new_ca = dict(name='fake-ca', address='fake-ca.some.url',
                vendor_id=simple_db['vendor'].id, serial_number='ABC123')
        res = testapp_login_disabled.post_json('/inventory/api/cas', new_ca)
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
                '/inventory/api/cas', params=new_ca, expect_errors=True)
        assert res.status_int == 404
        error_msg = 'not in inventory: vendor_id(%i)' % new_ca['vendor_id']
        assert error_msg in res.body


    def test_should_fail_to_create_duplicate_name_ca(
            self, testapp_login_disabled, simple_db):
        new_ca = dict(name=simple_db['ca'][0].name, address='fake-ca.some.url',
                vendor_id=simple_db['vendor'].id, serial_number='ABC123')
        res = testapp_login_disabled.post_json(
                '/inventory/api/cas', params=new_ca, expect_errors=True)
        assert res.status_int == 400
        error_msg = 'duplicate ca name(%s)' % new_ca['name']
        assert error_msg in res.body


    def test_should_fail_to_create_duplicate_ca_address(
            self, testapp_login_disabled, simple_db):
        new_ca = dict(name='fake-ca', address=simple_db['ca'][0].address,
                vendor_id=simple_db['vendor'].id, serial_number='ABC123')
        res = testapp_login_disabled.post_json(
                '/inventory/api/cas', params=new_ca, expect_errors=True)
        assert res.status_int == 400
        error_msg = 'duplicate ca address(%s)' % new_ca['address']
        assert error_msg in res.body


    def test_should_fail_to_create_duplicate_ca_serial_number(
            self, testapp_login_disabled, simple_db):
        new_ca = dict(name='fake-ca', address='fake-ca.some.url',
                vendor_id=simple_db['vendor'].id,
                serial_number=simple_db['ca'][1].serial_number)
        res = testapp_login_disabled.post_json(
                '/inventory/api/cas', params=new_ca, expect_errors=True)
        assert res.status_int == 400
        error_msg = 'duplicate ca serial_number(%s)' % new_ca['serial_number']
        assert error_msg in res.body


    def test_should_fail_to_update_duplicate_name_ca(
            self, testapp_login_disabled, simple_db):
        ca = dict(name=simple_db['ca'][0].name, address='fake-ca.some.url',
                vendor_id=simple_db['vendor'].id, serial_number='ABC123')
        res = testapp_login_disabled.put_json(
                '/inventory/api/cas/%i' % simple_db['ca'][1].id,
                params=ca, expect_errors=True)
        assert res.status_int == 400
        error_msg = 'duplicate ca name(%s)' % ca['name']
        assert error_msg in res.body


    def test_update_name_ca(
            self, testapp_login_disabled, simple_db):
        ca = dict(name='fake-name')
        res = testapp_login_disabled.put_json(
                '/inventory/api/cas/%i' % simple_db['ca'][1].id, params=ca)
        assert res.status_int == 201
        ca_updated = Ca.get_by_id(simple_db['ca'][1].id)
        assert ca_updated.name == ca['name']
