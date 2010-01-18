import thing
import command
import ircutils

@thing.facet_classes.register
class NameFacet(thing.ThingFacet):
    name = "name"    
    commands = command.thing.add_child(command.FacetCommandSet(name))
    
    @classmethod
    def does_attach(cls, thing):
        return True   
    
    @commands.add("{thing}", help="show information about {thing}")
    def describe(self, thing, context):
        context.reply(thing.describe(context))

@thing.presenters.register(set(["name"]), order=-10)
def present(thing, context):
    return "{name}".format(name = ircutils.bold(thing.name))
