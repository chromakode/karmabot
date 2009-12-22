import karmabot
import thing
import command
import ircutils

@thing.facet_classes.register
class KarmaBotFacet(thing.ThingFacet):
    name = "karmabot"
    listens = command.listen.create_child_set(name)
    
    @classmethod
    def does_attach(cls, thing):
        return thing.name == "karmabot"
        
@thing.presenters.register(set(["karmabot", "name", "karma", "description"]))
def present(thing, context):
    text = "{name}[v{version}]({karma}): {descriptions} ({things} things)".format(
        name         = ircutils.bold(thing.name),
        karma        = thing.facets["karma"].karma,
        descriptions = thing.facets["description"].present(),
        version      = karmabot.VERSION,
        things       = context.bot.things.count
    )
    return text
