# Copyright the Karmabot authors and contributors.
# All rights reserved.  See AUTHORS.
#
# This file is part of 'karmabot' and is distributed under the BSD license.
# See LICENSE for more details.
import time


class Cache:
    def __init__(self, func, expire_seconds=None):
        self.func = func
        self.expire_seconds = expire_seconds
        self.last_result = None
        self.last_time = None
        self.last_args = None
        self.last_kwargs = None

    def __call__(self, *args, **kwargs):
        call_time = time.time()
        if args != self.last_args or kwargs != self.last_kwargs or \
           self.last_time is None or call_time > self.last_time + self.expire_seconds:
            self.last_result = self.func(*args, **kwargs)
            self.last_time = call_time
            self.last_args = args
            self.last_kwargs = kwargs
        return self.last_result

    def reset(self):
        self.last_time = None


def created_timestamp(context):
    return {"who": context.nick, "when": time.time(), "where": context.where}
