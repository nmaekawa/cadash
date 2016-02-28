# -*- coding: utf-8 -*-
"""Test forms."""
from mock import patch

from cadash.public.forms import LoginForm
from cadash.user.models import BaseUser


@patch('cadash.ldap.LdapClient.is_authenticated', return_value=True)
@patch('cadash.ldap.LdapClient.fetch_groups', return_value=['can_bow','can_rollover'])
class TestLoginForm:
    """Login form."""

    def test_validate_success(self, mock_groups, mock_auth, testapp):
        """Login successful."""
        form = LoginForm(username='fake', password='example')
        assert form.validate() is True
        assert form.user.username == 'fake'
        assert form.user.is_in_group('can_bow')
        assert form.user.is_in_group('can_rollover')

    def test_validate_unknown_username(self, mock_groups, mock_auth, testapp):
        """Unknown username."""
        mock_auth.return_value = False
        form = LoginForm(username='unknown', password='example')
        assert form.validate() is False
        assert 'Unknown username:password combination' in form.username.errors
        assert form.user is None
