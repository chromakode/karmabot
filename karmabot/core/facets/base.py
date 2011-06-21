# Copyright the Karmabot authors and contributors.
# All rights reserved.  See AUTHORS.
#
# This file is part of 'karmabot' and is distributed under the BSD license.
# See LICENSE for more details.


class Facet(object):
    name = None
    commands = None
    listens = None
    display_key = -1

    def __init__(self, subject):
        self.subject = subject
        if self.does_attach(subject):
            subject.add_facet(self)
            self.on_attach()

    def __str__(self):
        return self.name

    @property
    def data(self):
        return self.subject.data.setdefault(self.name, {})

    def does_attach(self, subject):
        raise NotImplementedError

    def on_attach(self):
        pass

    def present(self, context):
        return u""
