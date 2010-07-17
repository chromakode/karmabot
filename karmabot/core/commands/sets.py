
from itertools import chain
import re

from .command import Command, CommandParser


class CommandSet(object):

    def __init__(self, name, regex_format="{0}", parent=None):
        self.name = name
        self.regex_format = regex_format
        self.parent = parent
        self.children = []
        self.commands = []

    def __iter__(self):
        return iter(self.commands)

    def add_child(self, command_set):
        command_set.parent = self
        self.children.append(command_set)
        return command_set

    def add(self, format, help_str, exclusive=False, visible=True):
        def decorator(f):
            self.commands.append(
                Command(self, format, f, help_str, visible, exclusive))
            return f
        return decorator

    def compile(self):

        def traverse_commands(cmdset):
            child_commands = (child.commands for child in cmdset.children)
            for command in chain(cmdset.commands, *child_commands):
                yield command

        command_infos = []
        for command in traverse_commands(self):
            regex = command.to_regex()
            formatted_regex = self.regex_format.format(regex)

            command_info = {"re": re.compile(formatted_regex, re.U),
                            "command": command,
                            "exclusive": command.exclusive}
            command_infos.append(command_info)

        # Sort exclusive commands before non-exclusive ones
        command_infos.sort(key=lambda c: c["exclusive"], reverse=True)

        return CommandParser(command_infos)
