# Copyright the Karmabot authors and contributors.
# All rights reserved.  See AUTHORS.
#
# This file is part of 'karmabot' and is distributed under the BSD license.
# See LICENSE for more details.

from .base import Facet


class KarmaBotFacet(Facet):
    name = "karmabot"

    @classmethod
    def does_attach(cls, thing):
        return thing.name == "karmabot"

    #TODO: add save/reload/quit commands, customizable messages and behavior
