from nio.modules.persistence import Persistence as PersistenceModule
from nio.modules.scheduler import Job
from nio.properties import TimeDeltaProperty, BoolProperty


class Persistence(object):

    """ A block mixin that provides persistence for some variables.

    To use, override the persisted_values function and define which variables
    on your class you wish to have persisted. The values should be strings
    that correspond to the variable names to be saved.

    """

    backup_interval = TimeDeltaProperty(
        visible=False, title='Backup Interval', default={"seconds": 60 * 60})
    load_from_persistence = BoolProperty(
        title='Load from Persistence?', default=True, advanced=True, order=100
    )

    def __init__(self):
        super().__init__()
        self._persistence = None
        self._backup_job = None
        self._warn_on_override("persistence_serialize", "persisted_values")
        self._warn_on_override("persistence_deserialize", "persisted_values")

    def persisted_values(self):
        """ Return a list containing the values to be persisted.

        This function should be overriden in a Block that wishes to use
        persistence. Return a list of the names of the instance level variables
        to save.

        For example, if your block class has an instance level attribute called
        `_values` and you wish to save it, you would return this list:
            ["_values"]
        """
        return []

    def _load(self):
        """ Load the values from persistence

        Item is loaded from persistence using block id, once item
        is loaded, all persisted values are examined against loaded
        item, if it exists, such value is then set as an attribute
        in the block instance
        """
        self.logger.debug("Loading from persistence")
        # load whole item from persistence
        data = self._persistence.load(self.id(), default={})
        if not data:
            return

        try:
            self.persistence_deserialize(data)
        except NotImplementedError:
            # allow backwards compatibility or persisted_values way
            for persisted_var in self.persisted_values():
                if persisted_var in data:
                    self.logger.debug("Loaded value {} for attribute {}".format(
                        data[persisted_var], persisted_var))
                    # Set the loaded value to the attribute on this class
                    setattr(self, persisted_var, data[persisted_var])
        except:
            # log exception while loading and let it continue
            self.logger.exception(
                "Failed to deserialize block with data: {}".format(data))

    def _save(self):
        """ Save the values to persistence
        """
        self.logger.debug("Saving to persistence")
        try:
            data = self.persistence_serialize()
        except NotImplementedError:
            # allow backwards compatibility or persisted_values way
            # generate item to be persisted by gathering all variables
            # to be persisted into a dictionary
            data = {persisted_var: getattr(self, persisted_var)
                    for persisted_var in self.persisted_values()}

        # save generated dictionary under block's id
        self._persistence.save(data, self.id())

    def configure(self, context):
        super().configure(context)
        # Create a persistence object using the block's id
        self._persistence = PersistenceModule()
        if self.load_from_persistence():
            self._load()

    def start(self):
        super().start()

        # If we have configured a backup interval, set up the job to
        # periodically save to persistence
        if self.backup_interval().total_seconds() > 0:
            self._backup_job = Job(self._save, self.backup_interval(), True)

    def stop(self):
        if self._backup_job:
            self._backup_job.cancel()

        # Do one last save before stopping
        self._save()
        super().stop()

    def persistence_serialize(self):
        """ Serializes block data

        Block developer should override this method by saving data it expects
        to have available next time the service is started

        Note: 'persistence_deserialize' method will read this data and
        populate block accordingly

        Returns: bytes or dict suitable for being persisted according to the
        persistence module implementation (e.g., file system, redis)
        """
        raise NotImplementedError

    def persistence_deserialize(self, data):
        """ De-serializes block data

        Args:
          data: The persisted data this block saved previously.

        Block developer should override this method by parsing data in order
        to populate block accordingly

        This method should take this persisted data and set the relevant
        state or class attributes for the block.

        """

        raise NotImplementedError

    def _is_method_overridden(self, method):
        if method in Persistence.__dict__ and method in self.__class__.__dict__:
            return \
                Persistence.__dict__[method] != self.__class__.__dict__[method]
        return False

    def _warn_on_override(self, method1, method2):
        if self._is_method_overridden(method1) and \
                self._is_method_overridden(method2):
            self.logger.warning(
                "Detected an override of both methods: '{0}' and '{1}', "
                "method: '{1}' will be ignored".format(method1, method2))
