# Copyright the Karmabot authors and contributors.
# All rights reserved.  See AUTHORS.
#
# This file is part of 'karmabot' and is distributed under the BSD license.
# See LICENSE for more details.
from karmabot.core.commands import CommandSet, listen, thing
from karmabot.core.thing import ThingFacet


class IRCChannelFacet(ThingFacet):
    name = "ircchannel"
    commands = thing.add_child(CommandSet(name))

    @classmethod
    def does_attach(cls, thing):
        return thing.name.startswith("#")

    @commands.add(u"join {thing}", help_str=u"join the channel {thing}")
    def join(self, thing, context):
        context.bot.join_with_key(thing.name.encode("utf-8"))

    @commands.add(u"leave {thing}", help_str=u"leave the channel {thing}")
    def leave(self, thing, context):
        channel = thing.name.encode("utf-8")
        context.reply("Bye!", where=channel)
        context.bot.leave(channel)

    # @commands.add("set topic of {thing} to {topic}",
    #               help_str="set the channel topic of {thing}")
    # def set_topic(self, thing, topic, context):
    #     channel = thing.name.encode("utf-8")
    #     topic = topic.encode("utf-8")
    #     context.bot.topic(channel, topic)

    @property
    def topic(self):
        return self.data.get("topic", None)

    @topic.setter
    def topic(self, value):
        self.data["topic"] = value


class IRCUserFacet(ThingFacet):
    #TODO: IRCUser facet, with trusted/admin types and verified hostmasks
    name = "ircuser"

    @classmethod
    def does_attach(cls, thing):
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
        user_thing = context.bot.things.get_thing(context.nick, context)
        user_thing.add_facet("ircuser")
