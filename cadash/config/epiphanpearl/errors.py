# -*- coding: utf-8 -*-
"""exceptions in inventory module."""

from cadash.errors import Error


class MalformedJsonError(Error):
    """returned json from epiphan is malformed or not as expected."""

