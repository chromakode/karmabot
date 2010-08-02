from karmabot.core import ircutils
from karmabot.core.client import thing
from karmabot.core.commands.sets import CommandSet
from karmabot.core.thing import ThingFacet
from karmabot.core.register import facet_registry, presenter_registry


@facet_registry.register
class NameFacet(ThingFacet):
    name = "name"
    commands = thing.add_child(CommandSet(name))

    @classmethod
    def does_attach(cls, thing):
        return True

    @commands.add(u"{thing}\?*", help_str=u"show information about {thing}")
    def describe(self, context, thing):
        # this is a thing object not the list of things
        context.reply(thing.describe(context))


@presenter_registry.register(set(["name"]), order=-10)
def present(thing, context):
    return u"{name}".format(name=ircutils.bold(thing.name))
