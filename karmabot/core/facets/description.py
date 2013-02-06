# Copyright the Karmabot authors and contributors.
# All rights reserved.  See AUTHORS.
#
# This file is part of 'karmabot' and is distributed under the BSD license.
# See LICENSE for more details.
from twisted.python import log

from .base import Facet
from ..commands import CommandSet, action
from ..utils import created_timestamp


class DescriptionFacet(Facet):
    name = "description"
    commands = action.add_child(CommandSet(name))
    display_key = 3

    @classmethod
    def does_attach(cls, subject):
        return True

    @commands.add(u"{subject} is {description}",
                  u"add a description to {subject}")
    def description(self, context, subject, description):
        self.data.append({"created": created_timestamp(context),
                                  "text": description})

    @commands.add(u"forget that {subject} is {description}",
                  u"drop a {description} for {subject}")
    def forget(self, context, subject, description):
        log.msg(self.descriptions)
        for desc in self.descriptions:
            if desc["text"] == description:
                self.descriptions.remove(desc)
                log.msg("removed %s" % desc)

    @property
    def data(self):
        return self.subject.data.setdefault(self.name, [])

    @property
    def descriptions(self):
        return self.data

    def present(self, context):
        return (u", ".join(desc["text"] for desc in self.descriptions)
                or u"<no description>")
