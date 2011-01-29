# Copyright the Karmabot authors and contributors.
# All rights reserved.  See AUTHORS.
#
# This file is part of 'karmabot' and is distributed under the BSD license.
# See LICENSE for more details.

from karmabot.core import VERSION
from .base import Facet


#TODO: add save/reload/quit commands, customizable messages and behavior
class KarmaBotFacet(Facet):
    name = "karmabot"

    def does_attach(self, thing):
        return thing.name == "karmabot"

    def present(thing, context):
        output = u"{name}[v{version}]({karma}): {descriptions} ({things} things)"
        text = output.format(
            name=thing.describe(context, facets=set(["name"])),
            karma=thing.facets["karma"].karma,
            descriptions=thing.facets["description"].present(),
            version=VERSION,
            things=len(context.bot.things),
            )
        return text
