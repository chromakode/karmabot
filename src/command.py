import re
import itertools

# TODO: regular expressions in this module should be
# replaced with something more robust and more efficient.

def thing_command(func, facet_name=None):
    def doit(thing, context, **arguments):
        thing = context.bot.things.get_thing(thing, context, with_facet=facet_name)
        arguments["thing"] = thing
        if thing:
            if facet_name:
                return func(arguments["thing"].facets[facet_name], 
                            context=context, **arguments)
            else:
                return func(context=context, **arguments)
        
    return doit

class CommandParser(object):

    def __init__(self, command_infos):
        self._command_infos = command_infos

    def handle_command(self, text, context, handled=False):
        for command_info in self._command_infos:
            match = command_info["re"].search(text)
            if match:
                substitution = self.dispatch_command(command_info["command"], match.groupdict(), context)
                handled = True             
                    
                if substitution:
                    # Start over with the new string
                    newtext = text[:match.start()] + substitution + text[match.end():]
                    return self.handle_command(newtext, context, True)
                
                if command_info["exclusive"]:
                    break                

        return (handled, text)
    
    def dispatch_command(self, command, arguments, context):
        return command.handler(context=context, **arguments)

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

    def add(self, format, help=None, visible=True, exclusive=False):
        def doit(handler):
            self.commands.append(Command(self, format, handler, help, visible, exclusive))
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

            command_info = {"re":        re.compile(formatted_regex, re.U),
                            "command":   command,
                            "exclusive": command.exclusive}
            command_infos.append(command_info)
        
        # Sort exclusive commands before non-exclusive ones
        command_infos.sort(key=lambda c:c["exclusive"], reverse=True)
        
        return CommandParser(command_infos)


class FacetCommandSet(CommandSet):
    def add(self, *args, **kwargs):
        def doit(handler):
            return CommandSet.add(self, *args, **kwargs)(thing_command(handler, self.name))
        
        return doit

# TODO: stripping listen commands such as --/++
class Command(object):

    def __init__(self, parent, format, handler, help=None, visible=True, exclusive=False):
        self.parent = parent
        self.format = format
        self.handler = handler
        self.help = help
        self.visible = visible
        self.exclusive = exclusive

    def to_regex(self):

        def sub_parameter(match):
            name = match.group(1)
            if name == "thing":
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

listen = CommandSet("listen")
thing = CommandSet("thing", regex_format="(^{0}$)")
