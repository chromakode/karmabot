import karmabot
import thing
import command
import ircutils

@thing.facet_classes.register
class HelpFacet(thing.ThingFacet):
    name = "help"
    commands = command.thing.create_child_set(name)
    
    @classmethod
    def does_attach(cls, thing):
        return True
    
    @commands.add("help {thing}", help="view command help for {thing}")
    def help(self, thing, context):
        help_lines = list()
        for facet in thing.facets.itervalues():
            if facet.commands:
                help_lines.extend("\"{0}\": {1}".format(cmd.format, cmd.help).replace("{thing}", thing.name) for cmd in facet.commands)
        
        context.reply("\n".join(help_lines))
