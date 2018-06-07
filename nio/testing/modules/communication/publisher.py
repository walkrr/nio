from nio.testing.modules.communication.manager import PubSubManager


class Publisher(object):

    """ A version of a Publisher useful for unit-testing """

    def __init__(self, topic=None, **kwargs):
        self.topic = topic

    def open(self, on_connected=None, on_disconnected=None):
        """ Opens publishing channel

        Args:
            on_connected (callable): function receiving notification when
                connection is established
            on_disconnected (callable): function receiving notification when
                a disconnection occurs

        This method delegates functionality to notify others the
        publisher creation and its definitions via a management signal.

        """
        PubSubManager.add_publisher(self)
        # on_connected, on_disconnected is not applicable,
        # testing communication module is always connected

    def is_connected(self):
        """ Determine if this publisher is connected and ready

        """
        return True

    def send(self, signals):
        """ Sends signals

        Args:
            signals: Signals to send
        """
        PubSubManager.send(self, signals)

    def close(self):
        """ Closes publisher.

        This method delegates functionality to notify others the
        publisher removal via a management signal.

        """
        PubSubManager.remove_publisher(self)

    def is_closed(self):
        """ Finds out if publisher has been closed """
        return self not in PubSubManager.publishers
