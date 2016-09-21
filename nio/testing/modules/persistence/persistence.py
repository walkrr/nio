class Store(object):
    """ Global store that allows to save persisted data across instances
    """
    values = {}
    collections = {}


class Persistence(object):

    """ An implementation of the Persistence proxy that works in memory.

    This will not actually persist any values, but will keep them in
    memory to make sure that save/load commands work properly.

    In other words, this will "persist" its data only as long as the current
    environment is active. This is useful in unit-tests and in environments
    where persistence is not desired, but it is hardly useful in practice.

    Persisted data is intended to remain available for all instances
    """

    def load(self, id, collection=None, default=None):
        if collection is not None:
            return Store.collections.get(collection, {}).get(id, default)
        else:
            return Store.values.get(id, default)

    def load_collection(self, collection, default=None):
        return Store.collections.get(collection, default)

    def save(self, item, id, collection=None):
        if collection is not None:
            if collection not in Store.collections:
                Store.collections[collection] = {}
            Store.collections[collection][id] = item
        else:
            Store.values[id] = item

    def save_collection(self, items, collection):
        Store.collections[collection] = items

    def remove(self, id, collection=None):
        if collection is not None:
            if collection in Store.collections and \
                            id in Store.collections[collection]:
                del Store.collections[collection][id]
        else:
            if id in Store.values:
                del Store.values[id]

    def remove_collection(self, collection):
        if collection in Store.collections:
            del Store.collections[collection]

    @classmethod
    def configure(cls, context):
        # clear Persistence store before each test starts
        Store.values = {}
        Store.collections = {}
