# Copyright the Karmabot authors and contributors.
# All rights reserved.  See AUTHORS.
#
# This file is part of 'karmabot' and is distributed under the BSD license.
# See LICENSE for more details.

import cPickle
from redis import Redis

from .facets import Facet
from .register import facet_registry


class Subject(object):

    def __init__(self, key, name):
        self.key = key
        self.name = name
        self.data = {"name": name,
                     "+facets": [],
                     "-facets": []}
        self.facets = {}
        facet_registry.attach(self, set(self.data["-facets"]))

    def add_facet(self, facet):
        if str(facet) in self.facets:
            return
        if not isinstance(facet, Facet):
            facet = facet_registry[facet](self)
        self.facets[str(facet)] = facet

    def remove_facet(self, facet):
        del self.facets[str(facet)]

    def iter_commands(self):
        for facet in self.facets.itervalues():
            for command_set in (facet.commands, facet.listens):
                if command_set:
                    for cmd in command_set:
                        yield cmd

    def describe(self, context):
        final_txt = u""
        sorted_facets = sorted(self.facets.itervalues(),
                               key=lambda x: x.display_key)
        for facet in sorted_facets:
            final_txt += facet.present(context)
        return final_txt


class Catalog(dict):
    def __init__(self, host='localhost', port=6379, db=0):
        self.redis = Redis(host=host, port=port, db=db)
        self.save = self.redis.save

    def __len__(self):
        return self.redis.dbsize()

    def get(self, key):
        subject = key.strip("() ")
        key = subject.lower()
        if self.redis.exists(key):
            subject = cPickle.loads(self.redis.get(key))
        else:
            subject = Subject(key, subject)
            self.set(key, subject)
        return subject

    def set(self, key, value):
        return self.redis.set(key,
                              cPickle.dumps(value, cPickle.HIGHEST_PROTOCOL))
