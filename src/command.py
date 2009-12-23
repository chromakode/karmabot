import re
import itertools

# TODO: regular expressions in this module should be
# replaced with something more robust and more efficient.


class CommandParser(object):

    def __init__(self, command_infos):
        self._command_infos = command_infos

    def iter_parses(self, text):
        for command_info in self._command_infos:
            match = command_info["re"].search(text)
            if match:
                yield command_info["command"], match.groupdict()
                if command_info["exclusive"]:
                    return

    def handle_command(self, text, context, thingstore):
        handled = False
        for command, arguments in self.iter_parses(text):
            if "thing" in arguments:
                thing_name = arguments["thing"].strip("()")
                facet_name = command.parent.name
                thing = thingstore.get_thing(thing_name, context,
                                             with_facet=facet_name)
                if thing:
                    arguments["thing"] = thing
                    command.handler(arguments["thing"].facets[facet_name],
                                    context=context, **arguments)
                    handled = True
            else:
                command.handler(context=context, **arguments)

        return handled


class CommandSet(object):

    def __init__(self, name, regex_format="{0}",
                 parent=None, exclusive=False):
        self.name = name
        self.regex_format = regex_format
        self.parent = parent
        self.exclusive = exclusive
        self.children = []
        self.commands = []

    def __iter__(self):
        return iter(self.commands)

    def create_child_set(self, name):
        cmdset = CommandSet(name, self)
        self.children.append(cmdset)
        return cmdset

    def add(self, format, help=None, visible=True):

        def doit(handler):
            self.commands.append(Command(self, format, handler, help, visible))
            return handler

        return doit

    def compile(self):

        def traverse_commands(cmdset):
            child_commands = (child.commands for child in cmdset.children)
            for command in itertools.chain(cmdset.commands, *child_commands):
                yield command

        command_infos = []
        for command in traverse_commands(self):
            regex = command.to_regex()
            formatted_regex = self.regex_format.format(regex)

            command_info = {
               "re": re.compile(formatted_regex),
                "command": command,
                "exclusive": self.exclusive,
               }
            command_infos.append(command_info)

        return CommandParser(command_infos)


# TODO: stripping listen commands such as --/++
class Command(object):

    def __init__(self, parent, format, handler, help=None, visible=True):
        self.parent = parent
        self.format = format
        self.handler = handler
        self.help = help
        self.visible = visible

    def to_regex(self):

        def sub_parameter(match):
            name = match.group(1)
            if name == "thing":
                parameter_regex = r"(?:\([#!?\w ]+\))|[#!?\w]+"
            else:
                # This regex may come back to haunt me.
                parameter_regex = r".+"

            return r"(?P<{name}>{regex})".format(name=name,
                                                 regex=parameter_regex)

        regex = self.format
        regex = regex.replace("+", r"\+")
        regex = re.sub(r"{(\w+)}", sub_parameter, regex)
        return regex

listen = CommandSet("listen", exclusive=True)
thing = CommandSet("thing", regex_format="(^{0}$)")
