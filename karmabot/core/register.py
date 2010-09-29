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

    def attach(self, thing, exclude=set()):
        for facet_class in self:
            if facet_class.name not in exclude:
                facet_class.attach(thing)


class PresenterRegistry(list):

    def _register(self, handled_facets, presenter, order=0):
        self.append(((set(handled_facets), order), presenter))

        # Sort by number of facets first, then order
        self.sort(key=lambda ((fs, o), p): (-len(fs), o))

    def register(self, handled_facets, order=0):
        def doit(presenter):
            self._register(handled_facets, presenter, order)
        return doit

    def get(self, handled_facets):
        for ((presenter_handled_facets, order), presenter) in self:
            if handled_facets == presenter_handled_facets:
                return presenter

    def iter_presenters(self, thing):
        # FIXME: This should be optimized
        facets = set(thing.facets.keys())
        for ((handled_facets, order), presenter) in self:
            if facets.issuperset(handled_facets):
                facets.difference_update(handled_facets)
                yield presenter

facet_registry = FacetRegistry()
presenter_registry = PresenterRegistry()
