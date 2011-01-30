# Copyright the Karmabot authors and contributors.
# All rights reserved.  See AUTHORS.
#
# This file is part of 'karmabot' and is distributed under the BSD license.
# See LICENSE for more details.

from karmabot.core.commands import CommandSet, listen, action
from .base import Facet


class IRCChannelFacet(Facet):
    name = "ircchannel"
    commands = action.add_child(CommandSet(name))

    @classmethod
    def does_attach(cls, subject):
        return subject.name.startswith("#")

    @commands.add(u"join {subject}", help_str=u"join the channel {subject}")
    def join(self, subject, context):
        context.bot.join_with_key(subject.name.encode("utf-8"))

    @commands.add(u"leave {subject}", help_str=u"leave the channel {subject}")
    def leave(self, subject, context):
        channel = subject.name.encode("utf-8")
        context.reply("Bye!", where=channel)
        context.bot.leave(channel)

    @commands.add(u"set topic of {subject} to {topic}",
                  u"set the channel topic of {subject}")
    def set_topic(self, context, subject, topic):
        channel = subject.name.encode("utf-8")
        topic = topic.encode("utf-8")
        context.bot.topic(channel, topic)

    @property
    def topic(self):
        return self.data.get("topic", None)

    @topic.setter
    def topic(self, value):
        self.data["topic"] = value

    def present(self, context):
        return u"Topic: {topic}".format(topic=self.topic)


class IRCUserFacet(Facet):
    #TODO: IRCUser facet, with trusted/admin types and verified hostmasks
    name = "ircuser"

    def does_attach(self, subject):
        # Attached by the listener
        return False

    @property
    def is_verified(self):
        return self.data.get("verified", False)

    @is_verified.setter
    def is_verified(self, value):
        self.data["verified"] = value

    @listen.add("u{message}",
                u'manage messages coming in')
    def message(self, context, **arg):
        user_subject = context.bot.subjects.get(context.nick)
        user_subject.add_facet("ircuser")
