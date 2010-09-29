# Copyright the Karmabot authors and contributors.
# All rights reserved.  See AUTHORS.
#
# This file is part of 'karmabot' and is distributed under the BSD license.
# See LICENSE for more details.

from karmabot.core.commands import CommandSet, thing
from karmabot.core.thing import ThingFacet


class NameFacet(ThingFacet):
    name = "name"
    commands = thing.add_child(CommandSet(name))

    @classmethod
    def does_attach(cls, thing):
        return True

    @commands.add(u"{thing}\?*", help_str=u"show information about {thing}")
    def describe(self, context, thing):
        # this is a thing object not the list of things
        context.reply(thing.describe(context))
