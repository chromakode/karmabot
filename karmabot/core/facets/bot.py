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
    display_key = 1

    def does_attach(self, subject):
        return subject.name == "karmabot"

    def present(self, context):
        return u"[v{0} - {1} subjects]".format(VERSION,
                                               len(context.bot.subjects))
