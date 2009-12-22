import sys
import time

try:
    import json
except ImportError:
    import simplejson as json

import command

def created_timestamp(context):
    return {"who":context.who, "when":time.time(), "where":context.where}

class ThingFacet(object):
    name = "thing"

    def __init__(self, thing):
        self._thing = thing
    
    @property
    def thing(self):
        return self._thing
    
    @property
    def data(self):
        return self.thing.data.setdefault(self.__class__.name, {})
    
    @classmethod
    def attach(cls, thing):
        if cls.does_attach(thing):
            facet = cls(thing)
            thing.add_facet(facet)
            facet.on_attach()
            
    @classmethod
    def does_attach(cls, thing):
        raise NotImplementedError
        
    def on_attach(self):
        pass
        
    def present(self):
        raise NotImplementedError

class FacetRegistry(dict):
    
    def register(self, facet_class):
        self[facet_class.name] = facet_class
        return facet_class
        
    def __iter__(self):
        return self.itervalues()
        
    def attach(self, thing, exclude=set()):
        for facet_class in self:
            if facet_class.name not in exclude:
                facet_class.attach(thing)
        
facet_classes = FacetRegistry()

class PresenterRegistry(list):
    
    def _register(self, handled_facets, presenter, order=0):
        self.append(((set(handled_facets), order), presenter))
        
        # Sort by number of facets first, then order
        self.sort(key=lambda ((fs,o),p): (-len(fs),o))
        
    def register(self, handled_facets, order=0):
        def doit(presenter):
            self._register(handled_facets, presenter, order)
        return doit
            
    def iter_presenters(self, thing):
        # FIXME: This should be optimized
        facets = set(thing.facets.keys())
        for ((handled_facets, order), presenter) in self:
            if facets.issuperset(handled_facets):
                facets.difference_update(handled_facets)
                yield presenter
                
presenters = PresenterRegistry()

class Thing(object):
    def __init__(self, thing_id, data):
        self._thing_id = thing_id
        self._data = data
        self._facets = dict()
        
        facet_classes.attach(self, self.data.get("-facets", set()))
        for facet_type in self.data.get("+facets", set()):
            facet = facet_classes[facet_type](self)
            self._add_facet(facet)
    
    @classmethod
    def create(self, thing_id, name, context):
        data = {"name":name, "created":created_timestamp(context)}
        thing = Thing(thing_id, data)
        return thing

    @property
    def thing_id(self):
        return self._thing_id
    
    @property
    def name(self):
        return self._data["name"]
        
    @property
    def data(self):
        return self._data
        
    @property
    def facets(self):
        return self._facets
        
    def add_facet(self, facet):
        self.facets[facet.__class__.name] = facet
        
    def describe(self, context):
        return "\n".join(filter(None, (presenter(self, context) for presenter in presenters.iter_presenters(self))))

class ThingStore(object):
    def __init__(self, filename):
        self.filename = filename
        self.data = None
        self.things = None
        
    def load(self):
        try:
            self.data = json.load(open(self.filename))
        except IOError:
            self.data = {"things":dict()}
        
        self.things = dict()
        for thing_id, thing_data in self.data["things"].iteritems():
            self.things[thing_id] = Thing(thing_id, thing_data)

    def save(self):
        json.dump(self.data, open(self.filename, "w"), sort_keys=True, indent=4)
        
    @property
    def count(self):
        return len(self.things)
        
    def _id_from_name(self, name):
        name = name.strip()
        thing_id = name.lower()
        return thing_id
        
    def get_thing(self, name, context, with_facet=None):
        name = name.strip()
        thing_id = self._id_from_name(name)
        
        if thing_id in self.things:
            thing = self.things[thing_id]
        else:
            thing = Thing.create(thing_id, name, context)
            
        if with_facet is not None and not with_facet in thing.facets:
            return None
        else:           
            self.things[thing_id] = thing
            self.data["things"][thing_id] = thing.data
            return self.things[thing_id]
