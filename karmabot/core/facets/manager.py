from karmabot.core import ircutils, VERSION

from ..register import facet_registry, presenter_registry

from .irc import IRCChannelFacet, IRCUserFacet
from .bot import KarmaBotFacet
from .name import NameFacet
from .description import DescriptionFacet
from .karma import KarmaFacet
from .help import HelpFacet


class FacetManager(object):
    core_facets = (IRCChannelFacet, IRCUserFacet,
                   KarmaFacet, KarmaBotFacet,
                   DescriptionFacet, HelpFacet,
                   NameFacet)

    def load_core(self):
        for facet in self.core_facets:
            facet_registry.register(facet)

    def load_extensions(self, extensions):
        for facet in extensions:
            __import__(facet)


@presenter_registry.register(set(["name", "description"]))
def present_name(thing, context):
    if thing.facets["description"].descriptions:
        text = u"{name}: {descriptions}".format(
            name=thing.describe(context, facets=set(["name"])),
            descriptions=thing.facets["description"].present())
        return text
    else:
        return thing.describe(context, facets=set(["name"]))


@presenter_registry.register(set(["name", "karma", "description"]))
def present_karma(thing, context):
    name_display = thing.describe(context, facets=set(["name", "karma"]))
    if thing.facets["description"].descriptions:
        text = u"{name}: {descriptions}".format(
            name=name_display,
            descriptions=thing.facets["description"].present())
        return text
    else:
        return u"no descriptions found for {name}".format(name=name_display)


@presenter_registry.register(set(["name", "karma"]))
def present(thing, context):
    text = u"{name}({karma})".format(
        name=thing.describe(context, facets=set(["name"])),
        karma=thing.facets["karma"].karma,
    )
    return text


@presenter_registry.register(set(["name"]), order=-10)
def present_strict_name(thing, context):
    return u"{name}".format(name=ircutils.bold(thing.name))


@presenter_registry.register(set(["karmabot", "name", "karma", "description"]))
def present_karmabot(thing, context):
    output_str = u"{name}[v{version}]({karma}): {descriptions} ({things} things)"
    text = output_str.format(
        name=thing.describe(context, facets=set(["name"])),
        karma=thing.facets["karma"].karma,
        descriptions=thing.facets["description"].present(),
        version=VERSION,
        things=context.bot.things.count,
        )
    return text


@presenter_registry.register(set(["ircchannel"]))
def present_channel(thing, context):
    facet = thing.facets["ircchannel"]
    if facet.topic:
        return u"Topic: {topic}".format(topic=facet.topic)
