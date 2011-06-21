# Copyright the Karmabot authors and contributors.
# All rights reserved.  See AUTHORS.
#
# This file is part of 'karmabot' and is distributed under the BSD license.
# See LICENSE for more details.

from karmabot.core.commands import CommandSet, action
from .base import Facet
from ..ircutils import bold


class NameFacet(Facet):
    name = "name"
    commands = action.add_child(CommandSet(name))
    display_key = 0

    def does_attach(cls, subject):
        return True

    @commands.add(u"{subject}\?*",
                  help_str=u"show information about {subject}")
    def describe(self, context, subject):
        # this is a subject object not the list of subjects
        context.reply(subject.describe(context))

    def present(self, context):
        return u"%s" % bold(self.subject.name)
