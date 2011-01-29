# Copyright the Karmabot authors and contributors.
# All rights reserved.  See AUTHORS.
#
# This file is part of 'karmabot' and is distributed under the BSD license.
# See LICENSE for more details.
import time
import cPickle
from redis import Redis

from .register import facet_registry, presenter_registry


def created_timestamp(context):
    return {"who": context.who, "when": time.time(), "where": context.where}


class ThingFacet(object):
    name = "thing"
    commands = None
    listens = None

    def __init__(self, thing):
        self.thing = thing
        if self.does_attach(thing):
            thing.add_facet(self)
            self.on_attach()

    def __str__(self):
        return self.name

    @property
    def data(self):
        return self.thing.data.setdefault(self.name, {})

    @data.deleter
    def data(self):
        if self.name in self.thing.data:
            del self.thing.data[self.name]

    @property
    def has_data(self):
        return self.name in self.thing.data

    @classmethod
    def does_attach(cls, thing):
        raise NotImplementedError

    def on_attach(self):
        pass

    def present(self):
        raise NotImplementedError


class Thing(object):

    def __init__(self, thing_id, name, context):
        self.thing_id = thing_id
        self.name = name
        self.data = {"name": name, "created": created_timestamp(context),
                     "+facets": []}
        self.facets = dict()

        facet_registry.attach(self, set(self.data.get("-facets", [])))
        for facet_type in set(self.facets):
            self.add_facet(facet_type)

    def add_facet(self, facet):
        if str(facet) in self.facets:
            return
        if not isinstance(facet, ThingFacet):
            facet = facet_registry[facet](self)
        self.facets[facet] = facet

    def remove_facet(self, facet):
        del self.facets[str(facet)]

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


class ThingStore(dict):

    def __init__(self, host='localhost', port=6379, db=0):
        self.host = host
        self.port = port
        self.db = db
        self.data = None
        self.redis = None

    def load(self):
        self.redis = Redis(host=self.host, port=self.port, db=self.db)

    def save(self):
        self.redis.save()

    @property
    def count(self):
        return self.redis.dbsize()

    def _id_from_name(self, name):
        name = name.strip()
        return name.lower()

    def add_thing(self, thing_id, thing):
        if not self.redis.exists(thing_id):
            self.redis.set(thing_id,
                           cPickle.dumps(thing, cPickle.HIGHEST_PROTOCOL))

    def get_thing(self, name, context, with_facet=None):
        name = name.strip("() ")
        thing_id = self._id_from_name(name)

        if self.redis.exists(thing_id):
            thing = cPickle.loads(self.redis.get(thing_id))
        else:
            thing = Thing(thing_id, name, context)

        if with_facet is not None and not with_facet in thing.facets:
            return None
        else:
            self.add_thing(thing_id, thing)
            return cPickle.loads(self.redis.get(thing_id))

    def set_thing(self, thing_id, thing):
        return self.redis.set(thing_id,
                               cPickle.dumps(thing, cPickle.HIGHEST_PROTOCOL))
