import thing
import command
import ircutils

@thing.facet_classes.register
class IRCChannelFacet(thing.ThingFacet):
    name = "ircchannel"    
    commands = command.thing.create_child_set(name)
    
    @classmethod
    def does_attach(cls, thing):
        return thing.name.startswith("#")
        
    @commands.add("join {thing}", help="join the channel {thing}")
    def join(self, thing, context):
        context.bot.join_with_key(thing.name.encode("utf-8"))
        
    @commands.add("leave {thing}", help="leave the channel {thing}")
    def join(self, thing, context):
        channel = thing.name.encode("utf-8")
        context.reply("Bye!", where=channel)
        context.bot.leave(channel)
        
    @property
    def topic(self):
        return self.data.get("topic", None)
        
    @topic.setter
    def topic(self, value):
        self.data["topic"] = value

@thing.presenters.register(set(["ircchannel"]))
def present(thing):
    facet = thing.facets["ircchannel"]
    if facet.topic:
        return "Topic: {topic}".format(topic=facet.topic)
