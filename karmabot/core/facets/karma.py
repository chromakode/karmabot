# Copyright the Karmabot authors and contributors.
# All rights reserved.  See AUTHORS.
#
# This file is part of 'karmabot' and is distributed under the BSD license.
# See LICENSE for more details.
from karmabot.core.client import listen, thing
from karmabot.core.thing import ThingFacet
from karmabot.core.commands.sets import CommandSet
from karmabot.core.register import facet_registry, presenter_registry


@facet_registry.register
class KarmaFacet(ThingFacet):
    name = "karma"
    listens = listen.add_child(CommandSet(name))

    @classmethod
    def does_attach(cls, thing):
        return True

    @listens.add(u"{thing}++", help_str=u"add 1 to karma")
    def inc(self, thing, context):
        self.data.setdefault(context.who, 0)
        self.data[context.who] += 1
        return thing.name

    @listens.add(u"{thing}--", help_str=u"subtract 1 from karma")
    def dec(self, thing, context):
        self.data.setdefault(context.who, 0)
        self.data[context.who] -= 1
        return thing.name

    @property
    def karma(self):
        return sum(self.data.itervalues())


@presenter_registry.register(set(["name", "karma"]))
def present(thing, context):
    text = u"{name}({karma})".format(
        name=thing.describe(context, facets=set(["name"])),
        karma=thing.facets["karma"].karma,
    )
    return text
