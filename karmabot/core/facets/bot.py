# Copyright the Karmabot authors and contributors.
# All rights reserved.  See AUTHORS.
#
# This file is part of 'karmabot' and is distributed under the BSD license.
# See LICENSE for more details.
from karmabot.core.client import VERSION
from karmabot.core import thing
from karmabot.core.register import facet_registry, presenter_registry


@facet_registry.register
class KarmaBotFacet(thing.ThingFacet):
    name = "karmabot"

    @classmethod
    def does_attach(cls, thing):
        return thing.name == "karmabot"

    #TODO: add save/reload/quit commands, customizable messages and behavior


@presenter_registry.register(set(["karmabot", "name", "karma", "description"]))
def present(thing, context):
    output_str = u"{name}[v{version}]({karma}): {descriptions} ({things} things)"
    text = output_str.format(
        name=thing.describe(context, facets=set(["name"])),
        karma=thing.facets["karma"].karma,
        descriptions=thing.facets["description"].present(),
        version=VERSION,
        things=context.bot.things.count,
        )
    return text
