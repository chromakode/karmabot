# Copyright the Karmabot authors and contributors.
# All rights reserved.  See AUTHORS.
#
# This file is part of 'karmabot' and is distributed under the BSD license.
# See LICENSE for more details.

import cPickle
from redis import Redis

from .facets import Facet
from .register import facet_registry
from .utils import created_timestamp


class Thing(object):

    def __init__(self, thing_id, name, context):
        self.thing_id = thing_id
        self.name = name
        self.data = {"name": name, "created": created_timestamp(context),
                     "+facets": [],
                     "-facets": []}
        self.facets = {}
        facet_registry.attach(self, set(self.data["-facets"]))

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
        final_txt = u""
        for facet in self.facets.itervalues():
            final_txt += facet.present(context)
        return final_txt


class ThingStore(dict):

    def __init__(self, host='localhost', port=6379, db=0):
        self.host = host
        self.port = port
        self.db = db
        self.data = None
        self.redis = Redis(host=self.host, port=self.port, db=self.db)
        self.save = self.redis.save

    def __len__(self):
        return self.redis.dbsize()

    def get(self, name, context, with_facet=None):
        name = name.strip("() ")
        thing_id = name.lower()
        if self.redis.exists(thing_id):
            thing = cPickle.loads(self.redis.get(thing_id))
        else:
            thing = Thing(thing_id, name, context)
            self.set(thing_id, thing)
        return thing

    def set(self, thing_id, thing):
        return self.redis.set(thing_id,
                              cPickle.dumps(thing, cPickle.HIGHEST_PROTOCOL))
