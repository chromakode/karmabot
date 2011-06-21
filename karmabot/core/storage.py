import cPickle
from redis import Redis

from .signal import post_connection
from .subject import Subject

db = None


@post_connection.connect
def load_catalog(sender):
    global db
    db = Catalog()


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
