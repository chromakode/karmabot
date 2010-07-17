from karmabot import thing
from karmabot import command

@thing.facet_classes.register
class KarmaFacet(thing.ThingFacet):
    name = "karma"
    listens = command.listen.add_child(command.FacetCommandSet(name))
    
    @classmethod
    def does_attach(cls, thing):
        return True
    
    @listens.add(u"{thing}++", help=u"add 1 to karma")
    def inc(self, thing, context):
        self.data.setdefault(context.who, 0)
        self.data[context.who] += 1
        return thing.name
        
    @listens.add(u"{thing}--", help=u"subtract 1 from karma")
    def dec(self, thing, context):
        self.data.setdefault(context.who, 0)
        self.data[context.who] -= 1
        return thing.name
        
    @property
    def karma(self):
        return sum(self.data.itervalues())

@thing.presenters.register(set(["name", "karma"]))
def present(thing, context):
    text = u"{name}({karma})".format(
        name  = thing.describe(context, facets=set(["name"])),
        karma = thing.facets["karma"].karma
    )
    return text
