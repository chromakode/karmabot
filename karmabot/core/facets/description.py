# Copyright the Karmabot authors and contributors.
# All rights reserved.  See AUTHORS.
#
# This file is part of 'karmabot' and is distributed under the BSD license.
# See LICENSE for more details.
from twisted.python import log

from .base import Facet
from ..commands import CommandSet, thing
from ..utils import created_timestamp


class DescriptionFacet(Facet):
    name = "description"
    commands = thing.add_child(CommandSet(name))

    @classmethod
    def does_attach(cls, thing):
        return True

    @commands.add(u"{thing} is {description}",
                  u"add a description to {thing}")
    def description(self, context, thing, description):
        self.data.append({"created": created_timestamp(context),
                                  "text": description})

    @commands.add(u"forget that {thing} is {description}",
                  u"drop a {description} for {thing}")
    def forget(self, context, thing, description):
        log.msg(self.descriptions)
        for desc in self.descriptions:
            if desc["text"] == description:
                self.descriptions.remove(desc)
                log.msg("removed %s" % desc)

    @property
    def descriptions(self):
        return self.data

    def present(self, context):
        return u", ".join(desc["text"] for desc in self.descriptions) \
            or u"<no description>"
