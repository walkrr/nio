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

    def open(self, on_connected=None, on_disconnected=None):
        """ Open a subscriber

        Args:
            on_connected (callable): function receiving notification when
                connection is established
            on_disconnected (callable): function receiving notification when
                a disconnection occurs

        When opening a subscriber the system will look for matches against
        existing publishers, when a match is found, a match is made
        so that signals published by matching publisher are received by this
        subscriber

        """
        raise NotImplementedError()

    def is_connected(self):
        """ Determine if this subscriber is connected and ready

        """
        raise NotImplementedError()

    def close(self):
        """ Close a subscriber.

        After closing it is expected all connections to publishers to be
        severed.

        """
        raise NotImplementedError()
