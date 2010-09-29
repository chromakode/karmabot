# Copyright the Karmabot authors and contributors.
# All rights reserved.  See AUTHORS.
#
# This file is part of 'karmabot' and is distributed under the BSD license.
# See LICENSE for more details.
# dedicated to LC

from json import JSONDecoder
from urllib import urlencode
from urllib2 import urlopen

from karmabot.core.client import thing
from karmabot.core.commands.sets import CommandSet
from karmabot.core.register import facet_registry
from karmabot.core.thing import ThingFacet

import re
import htmlentitydefs

##
# Function Placed in public domain by Fredrik Lundh
# http://effbot.org/zone/copyright.htm
# http://effbot.org/zone/re-sub.htm#unescape-html
# Removes HTML or XML character references and entities from a text string.
#
# @param text The HTML (or XML) source text.
# @return The plain text, as a Unicode string, if necessary.


def unescape(text):
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        # leave as is
        return text
    return re.sub("&#?\w+;", fixup, text)


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
            top_result = results.pop(0)
        context.reply(", ".join([unescape(top_result.get('titleNoFormatting')),
                                 top_result.get('unescapedUrl'),
                                 ]))
