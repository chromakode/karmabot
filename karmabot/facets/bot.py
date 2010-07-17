from karmabot import client
from karmabot import thing
from karmabot import command

@thing.facet_classes.register
class KarmaBotFacet(thing.ThingFacet):
    name = "karmabot"
    
    @classmethod
    def does_attach(cls, thing):
        return thing.name == "karmabot"
        
    #TODO: add save/reload/quit commands, customizable messages and behavior
        
@thing.presenters.register(set(["karmabot", "name", "karma", "description"]))
def present(thing, context):
    text = u"{name}[v{version}]({karma}): {descriptions} ({things} things)".format(
        name         = thing.describe(context, facets=set(["name"])),
        karma        = thing.facets["karma"].karma,
        descriptions = thing.facets["description"].present(),
        version      = karmabot.VERSION,
        things       = context.bot.things.count
    )
    return text
