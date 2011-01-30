# Copyright the Karmabot authors and contributors.
# All rights reserved.  See AUTHORS.
#
# This file is part of 'karmabot' and is distributed under the BSD license.
# See LICENSE for more details.

from .base import Facet
from karmabot.core.commands import CommandSet, action
from itertools import chain


def numbered(strs):
    return (u"{0}. {1}".format(num + 1, line)
            for num, line in enumerate(strs))


class HelpFacet(Facet):
    name = "help"
    commands = action.add_child(CommandSet(name))
    short_template = u"\"{0}\""
    full_template = short_template + u": {1}"

    @classmethod
    def does_attach(cls, subject):
        return True

    def get_topics(self, subject):
        topics = dict()
        for cmd in chain(action, subject.iter_commands()):
            if cmd.visible:
                topic = cmd.format.replace("{subject}", subject.name)
                help = cmd.help.replace("{subject}", subject.name)
                topics[topic] = help
        return topics

    def format_help(self, subject, full=False):
        line_template = self.full_template if full else self.short_template
        help_lines = [line_template.format(topic, help)
                      for topic, help in self.get_topics(subject).items()]
        help_lines.sort()
        return help_lines

    @commands.add(u"help {subject}",
                  help_str=u"view command help for {subject}")
    def help(self, context, subject):
        context.reply(u"Commands: " + u", ".join(self.format_help(subject)))

    @commands.add(u"help {subject} {topic}",
                  help_str=u"view help for {topic} on {subject}")
    def help_topic(self, context, subject, topic):
        topic = topic.strip(u"\"")
        topics = self.get_topics(subject)
        if topic in topics:
            context.reply(self.full_template.format(topic, topics[topic]))
        else:
            context.reply(u"I know of no such help topic.")
