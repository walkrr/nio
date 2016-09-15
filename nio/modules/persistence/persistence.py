from nio.modules.proxy import ModuleProxy


class Persistence(ModuleProxy):

    """ Persistence Module

    This class encapsulates the user-facing interface to NIO's
    persistence layer.

    Block writers use this module to save dynamic data at runtime, allowing
    it to persist in the block instance after a service/instance restart.

    Example:
        self.persistence.save(item, id) # saves the item
        item = self.persistence.load(id) # item is retrieved

    """

    def __init__(self):
        """ Create a Persistence object
        """
        super().__init__()

    def load(self, id, collection=None, default=None):
        """ Load an item from the persistence store.

        Args:
            id (str): Specifies the identifier of the item to load.
            collection (str): if provided, it specifies the collection the item
                belongs to.
            default: the value to return if the item does not exist

        Returns:
            item: The item associated with given id
        """
        raise NotImplementedError()

    def load_collection(self, collection, default=None):
        """ Load a collection from the persistence store.

        Args:
            collection (str): Specifies the collection to load
            default: the value to return if the collection does not exist

        Returns:
            items: The items associated with given collection
        """
        raise NotImplementedError()

    def save(self, item, id, collection=None):
        """ Save the item to the persistence store.

        Args:
            item: Item to save
            id (str): Specifies the identifier of the item to save.
            collection (str): if provided, it specifies the collection the item
                belongs to.
        """
        raise NotImplementedError()

    def save_collection(self, items, collection):
        """ Save a collection to the persistence store.

        Args:
            items: Items to save
            collection (str): Specifies the collection to save
        """
        raise NotImplementedError()

    def remove(self, id, collection=None):
        """ Remove an item from the persistence store.

        Args:
            id (str): Specifies the identifier of the item to remove.
            collection (str): if provided, it specifies the collection the item
                belongs to.
        """
        raise NotImplementedError()

    def remove_collection(self, collection):
        """ Remove a collection from the persistence store.

        Args:
            collection (str): Specifies the collection to remove
        """
        raise NotImplementedError()
