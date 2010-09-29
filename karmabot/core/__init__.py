# Copyright the Karmabot authors and contributors.
# All rights reserved.  See AUTHORS.
#
# This file is part of 'karmabot' and is distributed under the BSD license.
# See LICENSE for more details.
#

VERSION = "0.3"

from .facet_manager import FacetManager

facets = FacetManager()
facets.load_core()
