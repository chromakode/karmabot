from ..register import facet_registry

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
