import logging

from nio.util.nio_time import get_nio_time


class NIOFilter(logging.Filter):

    def filter(self, record):
        """  Filter the record before being logged

        We add niotime and context properties to the record so loggers
        created before the Logging Module initialization can be written
        using nio formatter
        """
        if not hasattr(record, 'niotime'):
            record.niotime = get_nio_time()
            record.context = record.name
        return True
