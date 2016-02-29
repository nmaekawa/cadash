# -*- coding: utf-8 -*-
"""Model unit tests."""
from cadash.user.models import BaseUser

class TestBaseUser:
    """BaseUser tests."""

    def setup(self):
        self.user = BaseUser('fake')
        self.user.place_in_groups(['can_read', 'can_edit', 'can_playdead'])


    def test_positive_belong_to_group(self):
        """test positive to belong to group."""
        assert self.user.is_in_group('can_playdead')
        assert self.user.is_in_group('can_read')
        assert self.user.is_in_group('can_edit')

    def test_negative_belong_to_group(self):
        """do not belong to group."""
        assert not self.user.is_in_group('potty_trained')
        assert self.user.is_in_group('can_edit')

    def test_add_new_group(self):
        """add a new group to groups user belong to."""
        self.user.place_in_groups(['potty_trained'])
        assert self.user.is_in_group('potty_trained')
        assert self.user.is_in_group('can_edit')
        assert not self.user.is_in_group('can_rollover')

    def test_add_duplicate_groups(self):
        """eliminate duplicates."""
        self.user.place_in_groups(
                ['can_playdead', 'can_playdead', 'can_playdead', 'can_edit'])
        assert len(self.user.groups) == 3

    def test_remove_group(self):
        """remove group."""
        self.user.remove_from_group('can_playdead')
        assert not self.user.is_in_group('can_playdead')
        assert self.user.is_in_group('can_edit')
        assert self.user.is_in_group('can_read')
        assert len(self.user.groups) == 2
