# Copyright the Karmabot authors and contributors.
# All rights reserved.  See AUTHORS.
#
# This file is part of 'karmabot' and is distributed under the BSD license.
# See LICENSE for more details.

from karmabot.core import thing


class KarmaBotFacet(thing.ThingFacet):
    name = "karmabot"

    @classmethod
    def does_attach(cls, thing):
        return thing.name == "karmabot"

    #TODO: add save/reload/quit commands, customizable messages and behavior
