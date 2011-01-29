# Copyright the Karmabot authors and contributors.
# All rights reserved.  See AUTHORS.
#
# This file is part of 'karmabot' and is distributed under the BSD license.
# See LICENSE for more details.


class Facet(object):
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

    def does_attach(self, thing):
        raise NotImplementedError

    def on_attach(self):
        pass

    def present(self, context):
        return u""
