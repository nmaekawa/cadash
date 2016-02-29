# -*- coding: utf-8 -*-
"""User models."""
from flask_login import UserMixin

class BaseUser(UserMixin):
    """base user of the app."""

    def __init__(self, username, password):
        """init user instance."""
        self._usr = username
        self._pwd = password
        self._grp = []

    @property
    def username(self):
        return self._usr

    @property
    def groups(self):
        return list(self._grp)

    def get_id(self):
        return unicode(self._usr)

    def is_in_group(self, group):
        """True if user belongs to `group`."""
        return group in self._grp

    def place_in_groups(self, groups):
        """add user to list `groups`. prevents duplicates"""
        self._grp = list(set(self._grp + groups))

    def remove_from_group(self, group):
        """remove single `group` from groups list."""
        try:
            self._grp.remove(group)
        except ValueError:  # group not present in _grp
            pass

    def __repr__(self):
        """represent instance as a unique string."""
        return '<BaseUser(%s)>' % self._usr
