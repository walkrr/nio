from nio.modules.proxy import ModuleProxy


class Persistence(ModuleProxy):

    """ Persistence Module

    This class encapsulates the user-facing interface to NIO's
    persistence layer. Block writers use this module to save dynamic
    data at runtime, allowing it to persist in the block instance
    after a service/instance restart.

    Args:
        name (str): The name of the block whose data will be persisted.

    Example:
        self.persistence.store('foo', 'bar')
        self.persistence.save() # saves the stored k/v store to disk
        val = self.persistence.load('foo') # now val == 'bar'

    """

    def __init__(self, name):
        """ Create a Persistence object for a given name """
        super().__init__(name)

    def store(self, key, value):
        """ Store a key/value datum in memory.

        Args:
            key: The key to store into
            value: The value associated with that key
        """
        raise NotImplementedError()

    def load(self, key, default=None):
        """ Load a value from the k/v store *currently in memory*.

        Args:
            key: The key to lookup in the store.
            default:  The value to return if the key is not present

        Returns:
            value: The value associated with that key

        """
        raise NotImplementedError()

    def has_key(self, key):
        """ Check whether a particular key exists in the persistence store

        Args:
            key: The key in question.

        Returns:
            exists (bool)

        """
        raise NotImplementedError()

    def clear(self, key):
        """ Remove the given key and associated value from the store

        As above, this will not be reflected permanently until
        Persistence.save is called.

        Args:
            key: The key pointing to the data to clear.
        """
        raise NotImplementedError()

    def save(self):
        """ Save the in-memory store to persistence.

        This allows the data therein to persist between instance/service
        restarts.
        """
        raise NotImplementedError()
