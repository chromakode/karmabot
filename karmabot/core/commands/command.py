# Copyright the Karmabot authors and contributors.
# All rights reserved.  See AUTHORS.
#
# This file is part of 'karmabot' and is distributed under the BSD license.
# See LICENSE for more details.
import re
from karmabot.core import storage


# TODO: regular expressions in this module should be
# replaced with something more robust and more efficient.

# TODO: stripping listen commands such as --/++
class Command(object):

    def __init__(self, parent, format, handler,
                 help=None, visible=True, exclusive=False):
        self.parent = parent
        self.format = format
        self.handler = handler
        self.help = help
        self.visible = visible
        self.exclusive = exclusive
        self.state = None

    def to_regex(self):
        def sub_parameter(match):
            name = match.group(1)
            if name == "subject":
                parameter_regex = r"(?:\([^()]+\))|[#!\w]+"
            else:
                # This regex may come back to haunt me.
                parameter_regex = r".+"

            return r"(?P<{name}>{regex})".format(name=name,
                                                 regex=parameter_regex)

        regex = self.format
        regex = regex.replace("+", r"\+")
        regex = re.sub(r"{(\w+)}", sub_parameter, regex)
        return regex


class CommandParser(object):

    def __init__(self, command_infos):
        self.command_infos = command_infos

    def __call__(self, text, context, handled=False):
        return self.handle_command(text, context, handled)

    def handle_command(self, text, context, handled=False):
        for command_info in self.command_infos:
            match = command_info["re"].search(text)

            if match:
                instance = None
                match_group = match.groupdict()
                subject = match_group.get('subject', None)
                command = command_info['command']
                match_group.update({'context': context})

                if subject:
                    match_group.update(
                        {'subject': storage.db.get(subject)})
                    handler_cls = command.handler.__module__.split('.').pop()
                    instance = match_group['subject'].facets.get(handler_cls)

                substitution = self.dispatch_command(command,
                                                     instance, match_group)
                handled = True
                if substitution:
                    # Start over with the new string
                    newtext = ''.join([text[:match.start()], substitution,
                                      text[match.end():]])
                    return self.handle_command(newtext, context, True)

                if command_info["exclusive"]:
                    break
        return (handled, text)

    def dispatch_command(self, command, instance, kw):
        if instance:
            context = kw.get('context')
            command.handler(instance, **kw)
            if context:
                storage.db.set(instance.subject.key,
                               instance.subject)
            return None
        else:
            return command.handler(command, **kw)
