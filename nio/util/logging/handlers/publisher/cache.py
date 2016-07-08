from nio.modules.module import ModuleNotInitialized
from nio.modules.proxy import ProxyNotProxied
from nio.util.cache import Cache


class LogCache(object):

    """ A cache of log messages to prevent logging loops.

    Maintains logging instructions per code source line helping
    avoid potential infinite loops when logging from a logging handler
    subscriber.

    The criteria consists of determining if a log record from the same
    source code line and with the same message is in the Cache.
    """

    def __init__(self, expire_interval):
        """ Create a new LogCache instance.

        Args:
            expire_interval (seconds): how long an entry is kept in cache

        """
        self._cache = Cache(expire_interval)

    def process_record(self, record):
        """ Processes a record against cache

        A record gets added to the cache when a record from same source code
        line containing the same message does not already exists in the cache

        Args:
            record: log record as incoming from logging module

        Returns:
            True: if record is present in cache
        """

        # determine key, which includes a hashed msg, and attempt to get record
        key = "{}-{}-{}".format(record.filename, record.lineno,
                                hash(record.msg))
        # determine if item with same message is present
        if self._cache.get(key):
            return True

        # record is always added or updated in cache under given key
        try:
            self._cache.add(key, record)
        except (ProxyNotProxied, ModuleNotInitialized):
            # catch any potential errors arising from the fact that
            # logging module starts before any other, i.e., scheduling
            pass

        return False
