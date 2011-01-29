# Copyright the Karmabot authors and contributors.
# All rights reserved.  See AUTHORS.
#
# This file is part of 'karmabot' and is distributed under the BSD license.
# See LICENSE for more details.
import urllib

try:
    import json
except ImportError:
    import simplejson as json

from karmabot import thing
from karmabot import command
from karmabot.utils import Cache


@thing.facet_classes.register
class RedditorFacet(thing.ThingFacet):
    name = "redditor"
    commands = command.thing.add_child(command.FacetCommandSet(name))

    def __init__(self, thing_):
        thing.ThingFacet.__init__(self, thing_)
        self.get_info = Cache(self._get_info, expire_seconds=10 * 60)

    @classmethod
    def does_attach(cls, thing):
        return False

    @commands.add(u"forget that {thing} is a redditor",
                  help=u"unset {thing}'s reddit username",
                  exclusive=True)
    def unset_redditor(self, thing, context):
        del self.data
        self.thing.remove_facet(self)

    @commands.add(u"{thing} has reddit username {username}",
                  help=u"set {thing}'s reddit username to {username}")
    def set_redditor_username(self, thing, username, context):
        self.username = username

    @property
    def username(self):
        if self.has_data and "username" in self.data:
            return self.data["username"]
        else:
            return self.thing.name

    @username.setter
    def username(self, value):
        if "username" not in self.data or value != self.data["username"]:
            self.data["username"] = value
            self.get_info.reset()

    def _get_info(self):
        about_url = "http://www.reddit.com/user/{0}/about.json"
        about = urllib.urlopen(about_url.format(self.username))
        return json.load(about)["data"]


@command.thing.add(u"{thing} is a redditor",
                   help=u"link {thing}'s reddit account to their user",
                   exclusive=True)
@command.thing_command
def set_redditor(thing, context):
    thing.add_facet(RedditorFacet)


@thing.presenters.register(set(["redditor"]))
def present(thing, context):
    info = thing.facets["redditor"].get_info()
    text = u"http://reddit.com/user/{name} ({link_karma}/{comment_karma})".format(
        name=info["name"],
        link_karma=info["link_karma"],
        comment_karma=info["comment_karma"])
    return text
