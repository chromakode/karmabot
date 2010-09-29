# Copyright the Karmabot authors and contributors.
# All rights reserved.  See AUTHORS.
#
# This file is part of 'karmabot' and is distributed under the BSD license.
# See LICENSE for more details.
from __future__ import print_function

import re
import json

format_handlers = dict()


def copy_keys(d, keys, mappings):
    result = dict((key, d[key]) for key in keys)
    for key, newkey in mappings.iteritems():
        result[newkey] = d[key]
    return result


def format_handler(from_format, to_format):
    def doit(handler):
        format_handlers[(from_format, to_format)] = handler
    return doit


@format_handler("1", "2")
def migrate_v1(old_data, filename):
    new_data = {"things": dict(), "version": "2"}
    thing_re = re.compile("^[#\w ]+$")
    for old_id, old_thing in old_data["things"].iteritems():
        if thing_re.match(old_id):
            new_thing = copy_keys(old_thing, ("name", "created"),
                                  {"desc": "description"})
            new_thing["karma"] = {"<unknown>": old_thing["karma"]}
            new_data["things"][old_id] = new_thing
    return new_data


def migrate(filename, to_format):
    data = json.load(open(filename))
    format = data.get("format", "1")
    return format_handlers[(format, to_format)](data, filename)


def main():
    from optparse import OptionParser
    parser = OptionParser(usage="usage: %prog [options] filenames")
    parser.add_option("-t", "--to-format",
                      action="store", dest="to_format", default="2",
                      help="format to migrate to")
    (options, filenames) = parser.parse_args()

    if not filenames:
        parser.error("No files specified.")

    for filename in filenames:
        print("Migrating {0}...".format(filename), end="")
        migrated_data = migrate(filename, options.to_format)
        new_filename = "migrated-{0}".format(filename)
        json.dump(migrated_data, open(new_filename, "w"),
                  sort_keys=True, indent=4)
        print(" done.")

if __name__ == "__main__":
    main()
