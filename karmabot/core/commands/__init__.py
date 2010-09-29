# Copyright the Karmabot authors and contributors.
# All rights reserved.  See AUTHORS.
#
# This file is part of 'karmabot' and is distributed under the BSD license.
# See LICENSE for more details.
#
from .sets import CommandSet

listen = CommandSet("listen")
thing = CommandSet("thing", regex_format="(^{0}$)")

__all__ = ['CommandSet', 'listen', 'thing']
