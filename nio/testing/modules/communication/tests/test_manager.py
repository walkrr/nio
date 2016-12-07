from unittest.mock import MagicMock
from nio.testing.modules.communication.manager import PubSubManager
from nio.testing import NIOTestCase


class TestTestingPubSubManager(NIOTestCase):

    def setUp(self):
        self.publisher = MagicMock()
        self.publisher.topic = "default_topic"
        self.subscriber = MagicMock()
        self.signals = [MagicMock()]
        PubSubManager.publishers[self.publisher] = [self.subscriber]

    def test_send_signals_with_topic(self):
        """Call handler with signals and topic if handler accepts that"""
        PubSubManager.send(self.publisher, self.signals)
        self.subscriber.handler.assert_called_once_with(
            self.signals, self.publisher.topic)

    def test_send_signals_without_topic(self):
        """Call handler with only signals if handler doesn't accept a topic"""
        def recv(signals):
            pass
        self.subscriber.handler.side_effect = recv
        PubSubManager.send(self.publisher, self.signals)
        self.subscriber.handler.assert_called_with(self.signals)
