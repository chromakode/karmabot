# Copyright the Karmabot authors and contributors.
# All rights reserved.  See AUTHORS.
#
# This file is part of 'karmabot' and is distributed under the BSD license.
# See LICENSE for more details.
__import__('pkg_resources').declare_namespace(__name__)

from .core import (
    client,
    commands,
    facets,
    ircutils,
    thing,
    register,
    utils,
)

__all__ = ['client', 'commands', 'facets', 'ircutils',
           'thing', 'register', 'utils']
