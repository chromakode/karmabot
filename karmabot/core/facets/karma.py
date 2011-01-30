# Copyright the Karmabot authors and contributors.
# All rights reserved.  See AUTHORS.
#
# This file is part of 'karmabot' and is distributed under the BSD license.
# See LICENSE for more details.

from .base import Facet
from karmabot.core.commands import CommandSet, listen


class KarmaFacet(Facet):
    name = "karma"
    listens = listen.add_child(CommandSet(name))
    display_key = 2

    def does_attach(self, thing):
        return True

    @listens.add(u"{thing}++", help_str=u"add 1 to karma")
    def inc(self, thing, context):
        self.data.setdefault(thing.name, 0)
        self.data[thing.name] += 1

    @listens.add(u"{thing}--", help_str=u"subtract 1 from karma")
    def dec(self, thing, context):
        self.data.setdefault(thing.name, 0)
        self.data[thing.name] -= 1

    def present(self, context):
        return u"({karma}): ".format(karma=self.data.get(self.thing.name, 0))
