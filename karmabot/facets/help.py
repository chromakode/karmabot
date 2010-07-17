from karmabot import thing
from karmabot import command
from itertools import chain

def numbered(strs):
    return (u"{0}. {1}".format(num+1, line) 
            for num, line in enumerate(strs))

@thing.facet_classes.register
class HelpFacet(thing.ThingFacet):
    name = "help"
    commands = command.thing.add_child(command.FacetCommandSet(name))
    
    short_template = u"\"{0}\"" 
    full_template = short_template + u": {1}"
    
    @classmethod
    def does_attach(cls, thing):
        return True
    
    def get_topics(self, thing):
        topics = dict()                    
        for cmd in chain(command.thing, thing.iter_commands()):
            if cmd.visible:
                topic = cmd.format.replace("{thing}", thing.name)
                help  = cmd.help.replace("{thing}", thing.name) 
                topics[topic] = help
        return topics
    
    def format_help(self, thing, full=False):
        line_template = self.full_template if full else self.short_template 
        help_lines = [line_template.format(topic, help) 
                      for topic, help in self.get_topics(thing).items()]
        help_lines.sort()
        return help_lines
    
    @commands.add(u"help {thing}", help=u"view command help for {thing}")
    def help(self, thing, context):
        context.reply(u"Commands: " + u", ".join(self.format_help(thing)))
        
    @commands.add(u"help {thing} {topic}", help=u"view help for {topic} on {thing}")
    def help_topic(self, thing, topic, context):
        topic = topic.strip(u"\"")
        topics = self.get_topics(thing)
        if topic in topics:
            context.reply(self.full_template.format(topic, topics[topic]))
        else:
            context.reply(u"I know of no such help topic.")
