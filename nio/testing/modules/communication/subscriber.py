from nio.testing.modules.communication.manager import PubSubManager


class Subscriber(object):

    """ A version of a Subscriber useful for unit-testing """

    def __init__(self, handler, topic=None, **kwargs):
        self.handler = handler
        self.topic = topic

    def open(self, on_connected=None, on_disconnected=None):
        """ Subscribes handler to matching publishers

        Args:
            on_connected (callable): function receiving notification when
                connection is established
            on_disconnected (callable): function receiving notification when
                a disconnection occurs

        """
        PubSubManager.add_subscriber(self)
        # on_connected, on_disconnected is not applicable,
        # testing communication module is always connected

    def is_connected(self):
        """ Determine if this subscriber is connected and ready

        """
        return True

    def close(self):
        """ Closes publisher.

        This method delegates functionality to notify others the
        subscriber removal via a management signal.

        """
        PubSubManager.remove_subscriber(self)
