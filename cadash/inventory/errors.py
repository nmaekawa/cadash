# -*- coding: utf-8 -*-
"""exceptions in inventory module."""

from cadash.errors import Error


class InvalidMhClusterEnvironmentError(Error):
    """mh cluster environment value is invalid."""

