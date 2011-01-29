# Copyright the Karmabot authors and contributors.
# All rights reserved.  See AUTHORS.
#
# This file is part of 'karmabot' and is distributed under the BSD license.
# See LICENSE for more details.
import time
import cPickle
from redis import Redis

from .facet import Facet
from .register import facet_registry, presenter_registry


def created_timestamp(context):
    return {"who": context.who, "when": time.time(), "where": context.where}


class Thing(object):

    def __init__(self, thing_id, name, context):
        self.thing_id = thing_id
        self.name = name
        self.data = {"name": name, "created": created_timestamp(context),
                     "+facets": [],
                     "-facets": []}
        self.facets = dict()

        facet_registry.attach(self, set(self.data["-facets"]))
        for facet in self.facets:
            self.add_facet(facet)

    def add_facet(self, facet):
        if str(facet) in self.facets:
            return
        if not isinstance(facet, Facet):
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
            return "\n".join(
                filter(None,
                       (presenter(self, context) for presenter
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

    def get_thing(self, name, context, with_facet=None):
        name = name.strip("() ")
        thing_id = name.lower()

        if self.redis.exists(thing_id):
            thing = cPickle.loads(self.redis.get(thing_id))
        else:
            thing = Thing(thing_id, name, context)
            self.set_thing(thing_id, thing)

        return thing

    def set_thing(self, thing_id, thing):
        return self.redis.set(thing_id,
                              cPickle.dumps(thing, cPickle.HIGHEST_PROTOCOL))
