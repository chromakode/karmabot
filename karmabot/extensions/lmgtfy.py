# dedicated to LC

from json import JSONDecoder
from urllib import urlencode
from urllib2 import urlopen

from karmabot.core.client import thing
from karmabot.core.commands.sets import CommandSet
from karmabot.core.register import facet_registry
from karmabot.core.thing import ThingFacet


@facet_registry.register
class LmgtfyFacet(ThingFacet):
    name = "lmgtfy"
    commands = thing.add_child(CommandSet(name))

    @classmethod
    def does_attach(cls, thing):
        return thing.name == "lmgtfy"

    @commands.add(u"lmgtfy {item}",
                  u"googles for a {item}")
    def lmgtfy(self, context, item):
        api_url = "http://ajax.googleapis.com/ajax/services/search/web?"
        response = urlopen(api_url + urlencode(dict(v="1.0",
                                                    q=item)))
        response = dict(JSONDecoder().decode(response.read()))
        top_result = {}
        if response.get('responseStatus') == 200:
            results = response.get('responseData').get('results')
            top_result = results.pop()
        context.reply(", ".join([top_result.get('titleNoFormatting'),
                                 top_result.get('unescapedUrl'),
                                 ]))
