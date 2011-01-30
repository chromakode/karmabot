# Copyright the Karmabot authors and contributors.
# All rights reserved.  See AUTHORS.
#
# This file is part of 'karmabot' and is distributed under the BSD license.
# See LICENSE for more details.


class FacetRegistry(dict):
    def register(self, facet_class):
        self[facet_class.name] = facet_class
        return facet_class

    def __iter__(self):
        return self.itervalues()

    def attach(self, subject, exclude=set()):
        for facet_class in self:
            if facet_class.name not in exclude:
                facet_class(subject)

facet_registry = FacetRegistry()
