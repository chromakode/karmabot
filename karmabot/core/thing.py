import time

try:
    import json
except ImportError:
    import simplejson as json

from .register import facet_registry, presenter_registry



def created_timestamp(context):
    return {"who": context.who, "when": time.time(), "where": context.where}


class ThingFacet(object):
    name = "thing"
    commands = None
    listens = None

    def __init__(self, thing):
        self._thing = thing

    @property
    def thing(self):
        return self._thing

    @property
    def data(self):
        return self.thing.data.setdefault(self.__class__.name, {})

    @data.deleter
    def data(self):
        if self.__class__.name in self.thing.data:
            del self.thing.data[self.__class__.name]

    @property
    def has_data(self):
        return self.__class__.name in self.thing.data

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


class Thing(object):

    def __init__(self, thing_id, data):
        self._thing_id = thing_id
        self._data = data
        self._facets = dict()

        facet_registry.attach(self, set(self.data.get("-facets", [])))
        for facet_type in set(self.data.get("+facets", [])):
            self.add_facet(facet_type)

    @classmethod
    def create(self, thing_id, name, context):
        data = {"name": name, "created": created_timestamp(context)}
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

    def _facet_type(self, facet):
        if isinstance(facet, ThingFacet):
            return facet.__class__.name
        elif isinstance(facet, (str, unicode)):
            return facet
        elif isinstance(facet, type) and issubclass(facet, ThingFacet):
            return facet.name
        else:
            raise TypeError

    def add_facet(self, facet):
        facet_type = self._facet_type(facet)
        if not isinstance(facet, ThingFacet):
            facet = facet_registry[facet_type](self)
        self.facets[facet_type] = facet

    def remove_facet(self, facet):
        del self.facets[self._facet_type(facet)]

    def attach_persistent(self, facet):
        facet_type = self._facet_type(facet)
        if facet_type not in self.data.setdefault("+facets", []):
            self.data["+facets"].append(facet_type)

        self.add_facet(facet_type)

    def detach_persistent(self, facet):
        facet_type = self._facet_type(facet)
        try:
            self.data.get("+facets", []).remove(facet_type)
        except ValueError:
            pass
        self.remove_facet(facet_type)

    def iter_commands(self):
        for facet in self.facets.itervalues():
            for command_set in (facet.commands, facet.listens):
                if command_set:
                    for cmd in command_set:
                        yield cmd

    def describe(self, context, facets=None):
        if facets:
            return presenter_registry.get(facets)(self, context)
        else:
            return "\n".join(filter(None,
                                    (presenter(self, context) \
                                         for presenter \
                                         in presenter_registry.iter_presenters(self))))


class ThingStore(object):
    FORMAT = "2"

    def __init__(self, filename):
        self.filename = filename
        self.data = None
        self.things = None

    def load(self):
        try:
            self.data = json.load(open(self.filename))
        except IOError:
            self.data = {"things": dict(), "version": ThingStore.FORMAT}

        self.things = dict()
        for thing_id, thing_data in self.data["things"].iteritems():
            self.things[thing_id] = Thing(thing_id, thing_data)

    def save(self):
        json.dump(self.data, open(self.filename, "w"),
                  sort_keys=True, indent=4)

    @property
    def count(self):
        return len(self.things)

    def _id_from_name(self, name):
        name = name.strip()
        thing_id = name.lower()
        return thing_id

    def add_thing(self, thing_id, thing):
        if not thing_id in self.things:
            self.things[thing_id] = thing
            self.data["things"][thing_id] = thing.data

    def get_thing(self, name, context, with_facet=None):
        name = name.strip("() ")
        thing_id = self._id_from_name(name)

        if thing_id in self.things:
            thing = self.things[thing_id]
        else:
            thing = Thing.create(thing_id, name, context)

        if with_facet is not None and not with_facet in thing.facets:
            return None
        else:
            self.add_thing(thing_id, thing)
            return self.things[thing_id]
