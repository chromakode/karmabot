# Copyright the Karmabot authors and contributors.
# All rights reserved.  See AUTHORS.
#
# This file is part of 'karmabot' and is distributed under the BSD license.
# See LICENSE for more details.
from karmabot.core.client import thing
from karmabot.core.register import facet_registry
from karmabot.core.thing import ThingFacet
from karmabot.core.commands.sets import CommandSet
from itertools import chain


def numbered(strs):
    return (u"{0}. {1}".format(num + 1, line)
            for num, line in enumerate(strs))


@facet_registry.register
class HelpFacet(ThingFacet):
    name = "help"
    commands = thing.add_child(CommandSet(name))
    short_template = u"\"{0}\""
    full_template = short_template + u": {1}"

    @classmethod
    def does_attach(cls, thing):
        return True

    def get_topics(self, this_thing):
        topics = dict()
        for cmd in chain(thing, this_thing.iter_commands()):
            if cmd.visible:
                topic = cmd.format.replace("{thing}", thing.name)
                help = cmd.help.replace("{thing}", thing.name)
                topics[topic] = help
        return topics

    def format_help(self, thing, full=False):
        line_template = self.full_template if full else self.short_template
        help_lines = [line_template.format(topic, help)
                      for topic, help in self.get_topics(thing).items()]
        help_lines.sort()
        return help_lines

    @commands.add(u"help {thing}",
                  help_str=u"view command help for {thing}")
    def help(self, context, thing):
        context.reply(u"Commands: " + u", ".join(self.format_help(thing)))

    @commands.add(u"help {thing} {topic}",
                  help_str=u"view help for {topic} on {thing}")
    def help_topic(self, context, thing, topic):
        topic = topic.strip(u"\"")
        topics = self.get_topics(thing)
        if topic in topics:
            context.reply(self.full_template.format(topic, topics[topic]))
        else:
            context.reply(u"I know of no such help topic.")
