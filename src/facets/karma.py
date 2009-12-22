import thing
import command
import ircutils

@thing.facet_classes.register
class KarmaFacet(thing.ThingFacet):
    name = "karma"
    listens = command.listen.create_child_set(name)
    
    @classmethod
    def does_attach(cls, thing):
        return True
    
    @listens.add("{thing}++", help="add 1 to karma")
    def inc(self, thing, context):
        self.data.setdefault(context.who, 0)
        self.data[context.who] += 1
        
    @listens.add("{thing}--", help="subtract 1 from karma")
    def dec(self, thing, context):
        self.data.setdefault(context.who, 0)
        self.data[context.who] -= 1
        
    @property
    def karma(self):
        return sum(self.data.itervalues())

@thing.presenters.register(set(["name", "karma"]))
def present(thing, context):
    text = "{name}({karma})".format(
        name  = ircutils.bold(thing.name),
        karma = thing.facets["karma"].karma
    )
    return text
    
    
@thing.presenters.register(set(["name", "karma", "description"]))
def present(thing, context):
    text = "{name}({karma}): {descriptions}".format(
        name         = ircutils.bold(thing.name),
        karma        = thing.facets["karma"].karma,
        descriptions = thing.facets["description"].present()
    )
    return text
