import re
import itertools

class CommandParser(object):
    def __init__(self, regex, command_index):
        self._regex = re.compile(regex, re.U)
        self._command_index = command_index
        
    def parse(self, text):
        match = self._regex.search(text)
        if match and match.lastindex:
            command, parameters = self._command_index[match.lastindex]
            
            parameter_values = match.group(*range(match.lastindex+1, match.lastindex+len(parameters)+1))
            if type(parameter_values) is not tuple:
                # Work around the fact that group() returns a string if only one item is requested
                parameter_values = [parameter_values]
            
            return command, dict(zip(parameters, parameter_values))
        else:
            return None, None
        
    def handle_command(self, text, context, thingstore):
        command, arguments = self.parse(text)
        if command:
            thing_name = arguments["thing"].strip("()")
            facet_name = command.parent.name
            thing = thingstore.get_thing(thing_name, context, with_facet=facet_name)
            if thing:
                arguments["thing"] = thing
                return command.handler(arguments["thing"].facets[facet_name], context=context, **arguments)

        return False

class CommandSet(object):
    def __init__(self, name, parent=None, search=False):
        self.name = name
        self.parent = parent
        self.children = []
        self.commands = []
        self.search = search
        
    def __iter__(self):
        return iter(self.commands)
        
    def create_child_set(self, name):
        cmdset = CommandSet(name, self)
        self.children.append(cmdset)
        return cmdset
        
    def add(self, format, help=None):
        def doit(handler):
            self.commands.append(Command(self, format, handler, help))
            return handler
        
        return doit
            
    def compile(self):
        def traverse_commands(cmdset):
            child_commands = (child.commands for child in cmdset.children)
            for command in itertools.chain(cmdset.commands, *child_commands):
                yield command
        
        command_index = dict()
        regexes = []
        group = 1
        for command in traverse_commands(self):
            regex, parameters = command.to_regex()
            
            group_format = "({0})" if self.search else "(^{0}$)"
            regexes.append(group_format.format(regex))
            command_index[group] = (command, parameters)
            
            group += 1 + len(parameters)
                
        return CommandParser("|".join(regexes), command_index)                

# TODO: stripping listen commands such as --/++
class Command(object):
    def __init__(self, parent, format, handler, help=None):
        self.parent = parent
        self.format = format
        self.handler = handler
        self.help = help
    
    def to_regex(self):
        parameters = []
        def sub_parameter(match):
            parameters.append(match.group(1))
            if match.group(1) == "thing":
                return r"((?:\([#!?\w ]+\))|[#!?\w]+)"
            else:
                return r"([!?'\w ]+)"
        
        regex = self.format
        regex = regex.replace("+", r"\+")
        regex = re.sub(r"{(\w+)}", sub_parameter, regex)
        return regex, parameters

listen = CommandSet("listen", search=True)
thing = CommandSet("thing")

