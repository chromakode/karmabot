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
    commands = command.thing.add_child(command.FacetCommandSet(name))
    
    @classmethod
    def does_attach(cls, thing):
        return False
        
    @commands.add("forget that {thing} is a redditor",
                  help="unset {thing}'s reddit username",
                  exclusive=True)
    def unset_redditor(self, thing, context):
        del self.data
        self.thing.detach_persistent(self)
        
    @commands.add("{thing} has reddit username {username}",
                  help="set {thing}'s reddit username to {username}")
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
        self.data["username"] = value
        
    def get_info(self):
        about_url = "http://www.reddit.com/user/{0}/about.json"
        about = urllib.urlopen(about_url.format(self.username))
        return json.load(about)["data"]

@command.thing.add("{thing} is a redditor",
                   help="link {thing}'s reddit account to their user",
                   exclusive=True)
@command.thing_command
def set_redditor(thing, context):
    thing.attach_persistent(RedditorFacet)

@thing.presenters.register(set(["redditor"]))
def present(thing, context):
    redditor = thing.facets["redditor"]
    info = thing.facets["redditor"].get_info()
    text = "http://reddit.com/user/{name} ({link_karma}/{comment_karma})".format(
        name          = info["name"],
        link_karma    = info["link_karma"],
        comment_karma = info["comment_karma"])
    return text
