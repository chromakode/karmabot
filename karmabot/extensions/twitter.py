# Copyright the Karmabot authors and contributors.
# All rights reserved.  See AUTHORS.
#
# This file is part of 'karmabot' and is distributed under the BSD license.
# See LICENSE for more details.
import urllib
from xml.sax.saxutils import unescape as unescape_html

try:
    import json
except ImportError:
    import simplejson as json
    
from karmabot import thing
from karmabot import command
from karmabot.utils import Cache

@thing.facet_classes.register
class TwitterFacet(thing.ThingFacet):
    name = "twitter"
    commands = command.thing.add_child(command.FacetCommandSet(name))
    
    def __init__(self, thing_):
        thing.ThingFacet.__init__(self, thing_)
        self.get_info = Cache(self._get_info, expire_seconds=10*60)
    
    @classmethod
    def does_attach(cls, thing):
        return False
        
    @commands.add(u"forget that {thing} is on twitter",
                  help=u"unset {thing}'s twitter username",
                  exclusive=True)
    def unset_twitterer(self, thing, context):
        del self.data
        self.thing.remove_facet(self)
        
    @commands.add(u"{thing} has twitter username {username}",
                  help=u"set {thing}'s twitter username to {username}")
    def set_twitter_username(self, thing, username, context):
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
        about_url = "http://api.twitter.com/1/statuses/user_timeline/{0}.json"
        about = urllib.urlopen(about_url.format(self.username))
        return json.load(about)
        
    def get_last_tweet(self):
        return unescape_html(self.get_info()[0]["text"])

@command.thing.add(u"{thing} is on twitter",
                   help=u"link {thing}'s twitter account to their user",
                   exclusive=True)
@command.thing_command
def set_twitterer(thing, context):
    thing.add_facet(TwitterFacet)

@thing.presenters.register(set(["twitter"]))
def present(thing, context):
    twitter = thing.facets["twitter"]
    text = u"@{twitter_name}: \"{tweet}\"".format(
        twitter_name = twitter.username,
        tweet        = twitter.get_last_tweet())
    return text
    
@thing.presenters.register(set(["name", "karma", "description", "twitter"]))
def present(thing, context):
    twitter = thing.facets["twitter"]
    name_display = thing.describe(context, facets=set(["name", "karma"]))
    text = u"{name} \"{tweet}\"{descriptions}".format(
        name         = name_display,
        tweet        = twitter.get_last_tweet(),
        descriptions = ": " + thing.facets["description"].present() 
                       if thing.facets["description"].descriptions else "")
    return text
