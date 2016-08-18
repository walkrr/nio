from nio.modules.proxy import ModuleProxy


class Subscriber(ModuleProxy):

    """ An interface for a generic Subscriber in the communication module """

    def __init__(self, handler, topic=None, **kwargs):
        """ Create a new subscriber instance.

        Args:
            handler: Specifies where signals will be received. A signature
                definition sample is provided below.

                def process_signals(self, signals)

            topic (str): Defines the kind of information to subscribe to.

            kwargs: Key value argument pairs, used for backwards compatibility.
        """
        super().__init__(handler, topic=topic, **kwargs)

    def open(self):
        """ Open a subscriber

        When opening a subscriber the system will look for matches against
        existing publishers, when a match is found, a 'connection' is made
        so that signals published by matching publisher are received by this
        subscriber

        """
        raise NotImplementedError()

    def close(self):
        """ Closes publisher.

        This method delegates functionality to notify others the
        subscriber removal via a management signal.

        """

        raise NotImplementedError()
