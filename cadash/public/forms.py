# -*- coding: utf-8 -*-
"""Public forms."""
from flask_wtf import Form
from wtforms import PasswordField
from wtforms import StringField
from wtforms.validators import DataRequired

from cadash.extensions import ldap_cli
from cadash.user.models import BaseUser


class LoginForm(Form):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        """Create instance."""
        super(LoginForm, self).__init__(*args, **kwargs)
        self.user = None

    def validate(self):
        """Validate the form."""
        initial_validation = super(LoginForm, self).validate()
        if not initial_validation:
            return False

        self.user = self._fetch_ldap_user(
                usr=self.username.data,
                pwd=self.password.data,
                cli=ldap_cli)
        if not self.user:
            self.username.errors.append('Unknown username:password combination')
            return False

        if not self.user.is_active:
            self.username.errors.append('User not activated')
            return False
        return True


    def _fetch_ldap_user(self, usr, pwd, cli):
        """fetch user in ldap, and the groups user belongs to.

        returns a BaseUser object or None if not authenticated or unknown
        """
        if cli.is_authenticated(usr, pwd):
            u = BaseUser(usr)
            groups = cli.fetch_groups(usr)
            u.place_in_groups(groups)
            return u
        else:
            return None

