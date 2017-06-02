from nio import Signal
from nio.testing import NIOTestCase
from nio.testing.modules.communication.publisher import Publisher
from nio.testing.modules.communication.subscriber import Subscriber


class TestTestingPublisher(NIOTestCase):

    def _signals_handler(self, signals):
        self._signals = signals

    def test_publisher(self):
        """ Asserts subscriber receives publisher signals
        """
        self._signals = None

        topic = "test"
        subscriber = Subscriber(self._signals_handler, topic=topic)
        subscriber.open()

        publisher = Publisher(topic=topic)
        publisher.open()
        signals = [Signal({"attr1": 1})]
        publisher.send(signals)
        # assert signal reception
        self.assertEqual(signals, self._signals)
        publisher.close()
        # assert publisher closure
        self.assertTrue(publisher.is_closed())

        subscriber.close()
