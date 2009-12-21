import thing
import command
import ircutils

created_timestamp = thing.created_timestamp

@thing.facet_classes.register
class DescriptionFacet(thing.ThingFacet):
    name = "description"
    commands = command.thing.create_child_set(name)
    
    @classmethod
    def does_attach(cls, thing):
        return True
    
    @commands.add("{thing} is {description}", help="add a description to {thing}")
    def describe(self, thing, description, context):
        self.descriptions.append({"created":created_timestamp(context), "text":description})
    
    @property
    def data(self):
        return self.thing.data.setdefault(self.__class__.name, [])
    
    @property
    def descriptions(self):
        return self.data
        
    def present(self):
        return ", ".join(desc["text"] for desc in self.descriptions) or "<no description>"

@thing.presenters.register(set(["name", "description"]))
def present(thing):
    text = "{name}: {descriptions}".format(
        name         = ircutils.bold(thing.name),
        descriptions = thing.facets["description"].present()
    )
    return text
