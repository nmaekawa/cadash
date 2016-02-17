# -*- coding: utf-8 -*-
"""Functional tests using WebTest.

See: http://webtest.readthedocs.org/
"""
import os

import httpretty
import json

from flask import url_for

from cadash.user.models import User
from tests.factories import UserFactory

data_filename = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 'ca_loc_shortmap.json')

def get_json_data():
    txt = open(data_filename, 'r')
    raw_data = txt.read()
    #json_data = json.loads(raw_data)
    txt.close()
    return raw_data


class TestLoggingIn:
    """Login."""

    def test_can_log_in_returns_200(self, user, testapp):
        """Login successful."""
        # Goes to homepage
        res = testapp.get('/')
        # Fills out login form in navbar
        form = res.forms['loginForm']
        form['username'] = user.username
        form['password'] = 'myprecious'
        # Submits
        res = form.submit().follow()
        assert res.status_code == 200

    def test_sees_alert_on_log_out(self, user, testapp):
        """Show alert on logout."""
        res = testapp.get('/')
        # Fills out login form in navbar
        form = res.forms['loginForm']
        form['username'] = user.username
        form['password'] = 'myprecious'
        # Submits
        res = form.submit().follow()
        res = testapp.get(url_for('public.logout')).follow()
        # sees alert
        assert 'You are logged out.' in res

    def test_sees_error_message_if_password_is_incorrect(self, user, testapp):
        """Show error if password is incorrect."""
        # Goes to homepage
        res = testapp.get('/')
        # Fills out login form, password incorrect
        form = res.forms['loginForm']
        form['username'] = user.username
        form['password'] = 'wrong'
        # Submits
        res = form.submit()
        # sees error
        assert 'Invalid password' in res

    def test_sees_error_message_if_username_doesnt_exist(self, user, testapp):
        """Show error if username doesn't exist."""
        # Goes to homepage
        res = testapp.get('/')
        # Fills out login form, password incorrect
        form = res.forms['loginForm']
        form['username'] = 'unknown'
        form['password'] = 'myprecious'
        # Submits
        res = form.submit()
        # sees error
        assert 'Unknown user' in res


class TestRegistering:
    """Register a user."""

    def test_can_register(self, user, testapp):
        """Register a new user."""
        old_count = len(User.query.all())
        # Goes to homepage
        res = testapp.get('/')
        # Clicks Create Account button
        res = res.click('Create account')
        # Fills out the form
        form = res.forms['registerForm']
        form['username'] = 'foobar'
        form['email'] = 'foo@bar.com'
        form['password'] = 'secret'
        form['confirm'] = 'secret'
        # Submits
        res = form.submit().follow()
        assert res.status_code == 200
        # A new user was created
        assert len(User.query.all()) == old_count + 1

    def test_sees_error_message_if_passwords_dont_match(self, user, testapp):
        """Show error if passwords don't match."""
        # Goes to registration page
        res = testapp.get(url_for('public.register'))
        # Fills out form, but passwords don't match
        form = res.forms['registerForm']
        form['username'] = 'foobar'
        form['email'] = 'foo@bar.com'
        form['password'] = 'secret'
        form['confirm'] = 'secrets'
        # Submits
        res = form.submit()
        # sees error message
        assert 'Passwords must match' in res

    def test_sees_error_message_if_user_already_registered(self, user, testapp):
        """Show error if user already registered."""
        user = UserFactory(active=True)  # A registered user
        user.save()
        # Goes to registration page
        res = testapp.get(url_for('public.register'))
        # Fills out form, but username is already registered
        form = res.forms['registerForm']
        form['username'] = user.username
        form['email'] = 'foo@bar.com'
        form['password'] = 'secret'
        form['confirm'] = 'secret'
        # Submits
        res = form.submit()
        # sees error
        assert 'Username already registered' in res


class TestRedunlive:
    """list location primary/backup ca's."""

    def test_displays_list_of_locations(self, user, testapp_login_disabled):
        """displays primary/backup ca for all locations."""
        httpretty.enable()
        self.register_uri_for_http()

        res = testapp_login_disabled.get('/redunlive/')

        assert 'fake_epiphan017' in res
        assert 'fake_epiphan033' in res

        radio = res.forms['fake_room']['active_device']
        assert radio.value == 'secondary'

        httpretty.disable()
        httpretty.reset()


    def test_toggle_backup_to_primary(self, user, testapp_login_disabled):
        """displays primary/backup ca for all locations."""
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
