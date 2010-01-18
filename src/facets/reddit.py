import urllib

try:
    import json
except ImportError:
    import simplejson as json
    
import thing
import command

@thing.facet_classes.register
class RedditorFacet(thing.ThingFacet):
    name = "redditor"
    commands = command.thing.create_child_set(name)
    
    @classmethod
    def does_attach(cls, thing):
        return True
    
    @commands.add("{thing} is a redditor",
                  help="set {thing}'s reddit username to their nick",
                  exclusive=True)
    def set_redditor(self, thing, context):
        self.username = thing.name
        
    @commands.add("forget that {thing} is a redditor",
                  help="unset {thing}'s reddit username",
                  exclusive=True)
    def unset_redditor(self, thing, context):
        del self.username
        
    @commands.add("{thing} has reddit username {username}",
                  help="set {thing}'s reddit username to {username}")
    def set_redditor_username(self, thing, username, context):
        self.username = username
    
    @property
    def username(self):
        if self.has_data:
            return self.data["username"]
        
    @username.setter
    def username(self, value):
        self.data["username"] = value
        
    @username.deleter
    def username(self):
        del self.data
        
    def get_info(self):
        about_url = "http://www.reddit.com/user/{0}/about.json"
        about = urllib.urlopen(about_url.format(self.data["username"]))
        return json.load(about)["data"]

@thing.presenters.register(set(["redditor"]))
def present(thing, context):
    redditor = thing.facets["redditor"]
    if redditor.username:
        info = thing.facets["redditor"].get_info()
        text = "http://reddit.com/user/{name} ({link_karma}/{comment_karma})".format(
            name          = info["name"],
            link_karma    = info["link_karma"],
            comment_karma = info["comment_karma"])
        return text
