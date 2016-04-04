# -*- coding: utf-8 -*-
"""Functional tests using WebTest.

See: http://webtest.readthedocs.org/
"""
import os

import httpretty
from flask import url_for
from mock import patch

data_filename = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 'ca_loc_shortmap.json')

def get_json_data():
    txt = open(data_filename, 'r')
    raw_data = txt.read()
    txt.close()
    return raw_data


@patch('cadash.ldap.LdapClient.is_authenticated', return_value=True)
@patch('cadash.ldap.LdapClient.fetch_groups', return_value=['can_bow','can_rollover'])
class TestLoggingIn(object):
    """Login."""

    def test_can_log_in_returns_200(self, mock_groups, mock_auth, testapp):
        """Login successful."""
        # Goes to homepage
        res = testapp.get('/')
        # Fills out login form in navbar
        form = res.forms['loginForm']
        form['username'] = 'fake'
        form['password'] = 'example'
        # Submits
        res = form.submit().follow()
        assert res.status_code == 200

    def test_sees_alert_on_log_out(self, mock_groups, mock_auth, testapp):
        """Show alert on logout."""
        res = testapp.get('/')
        # Fills out login form in navbar
        form = res.forms['loginForm']
        form['username'] = 'fake'
        form['password'] = 'example'
        # Submits
        res = form.submit().follow()
        res = testapp.get(url_for('public.logout')).follow()
        # sees alert
        assert 'You are logged out.' in res

    def test_sees_error_msg_if_usr_pwd_combination_incorrect(self, mock_groups, mock_auth, testapp):
        """Show error if password is incorrect."""
        # Goes to homepage
        res = testapp.get('/')
        # Fills out login form, password incorrect
        form = res.forms['loginForm']
        form['username'] = 'fake'
        form['password'] = 'wrong'
        mock_auth.return_value = False
        # Submits
        res = form.submit()
        # sees error
        assert 'Unknown username:password combination' in res


class TestRedunlive(object):
    """list location primary/backup ca's."""

    def test_displays_list_of_locations(self, testapp_login_disabled):
        """display primary/backup ca for all locations."""
        httpretty.enable()
        self.register_uri_for_http()

        res = testapp_login_disabled.get('/redunlive/')

        assert 'fake_epiphan017' in res
        assert 'fake_epiphan033' in res

        radio = res.forms['fake_room']['active_device']
        assert radio.value == 'secondary'

        httpretty.disable()
        httpretty.reset()


    def test_toggle_backup_to_primary(self, testapp_login_disabled):
        """display primary/backup ca for all locations."""
        httpretty.enable()
        self.register_uri_for_http()

        res = testapp_login_disabled.get('/redunlive/')
        form = res.forms['fake_room']
        form['active_device'] = 'primary'

        # toggle active_device from secondary to primary
        res = form.submit()

        radio = res.forms['fake_room']['active_device']
        assert radio.value == 'primary'

        httpretty.disable()
        httpretty.reset()


    def register_uri_for_http(self):
        """register uri's for a normal request of redunlive homepage."""
        # pull info on all locations and cas via ca_stats
        httpretty.register_uri(
                httpretty.GET,
                'http://ca_stats_fake_url.com',
                body=get_json_data())
        # check each ca
        httpretty.register_uri(
                httpretty.GET,
                'http://fake-epiphan033.dce.harvard.edu/admin/channel3/get_params.cgi',
                responses=[
                    httpretty.Response(body='publish_type = 0'),
                    httpretty.Response(body='publish_type = 6')]
                )
        httpretty.register_uri(
                httpretty.GET,
                'http://fake-epiphan033.dce.harvard.edu/admin/channel4/get_params.cgi',
                body='publish_type = 6')
        # fix live/lowBR divergent live stream status:
        # live has precedence, so it sets lowBR channel publish_type to 0
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
        httpretty.register_uri(
                httpretty.GET,
                'http://fake-epiphan017.dce.harvard.edu/admin/channel3/set_params.cgi',
                body='', status=201)
        httpretty.register_uri(
                httpretty.GET,
                'http://fake-epiphan017.dce.harvard.edu/admin/channel4/set_params.cgi',
                body='', status=201)
        httpretty.register_uri(
                httpretty.GET,
                'http://fake-epiphan033.dce.harvard.edu/admin/channel3/set_params.cgi',
                body='', status=201)
