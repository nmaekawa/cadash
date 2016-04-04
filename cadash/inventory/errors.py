# -*- coding: utf-8 -*-
"""exceptions in inventory module."""

from cadash.errors import Error


class InvalidMhClusterEnvironmentError(Error):
    """mh cluster environment value is invalid."""


class InvalidCaRoleError(Error):
    """role must be in cadash.inventory.models.CA_ROLES."""


class InvalidOperationError(Error):
    """can't execute given operation in this object."""


class AssociationError(Error):
    """can't associate entities due to some constraint."""


class MissingVendorError(Error):
    """vendor is not in inventory."""
