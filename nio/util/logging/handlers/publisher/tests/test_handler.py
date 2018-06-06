from nio.modules.communication.subscriber import Subscriber
from nio.util.logging.handlers.publisher.handler import PublisherHandler
from nio.util.logging.handlers.publisher.proxy import PublisherProxy

from nio.testing.test_case import NIOTestCase
from nio.util.logging.handlers.publisher.tests import LogRecordTest, lineno
from datetime import datetime
from time import monotonic


class TestHandler(NIOTestCase):

    def get_test_modules(self):
        return super().get_test_modules() | {'communication'}

    def setUp(self):
        self._received_messages = []
        # Set up our publisher handler with the proper filters and handlers

        publisher_topic = "nio_logging"
        self._handler = PublisherHandler(
            topic=publisher_topic, publisher_ready_wait_interval_time=0.01)

        # Want to create our PublisherHandler before we call super setup,
        # the handler will initialize the PublisherProxy which should be
        # done before the modules are ready
        super().setUp()

        # Set up a test-wide handler for messages delivered through the
        # publisher
        self._subscriber = Subscriber(self._on_logger_signal,
                                      topic=publisher_topic)
        self._subscriber.open()

    def tearDown(self):
        self._subscriber.close()
        self._handler.close()
        self._received_messages = []
        super().tearDown()

    def test_handler(self):
        """ Asserts that messages are published """

        # wait for publisher to be ready
        self.assertTrue(PublisherProxy._publisher_ready_event.wait(1))

        messages = ["message1", "message2"]
        for message in messages:
            self._handler.emit(
                LogRecordTest(__file__, lineno(), message))

        for message in messages:
            self.assertIn(message, self._received_messages)

    def _on_logger_signal(self, signals):
        for signal in signals:
            self._received_messages.append(signal.message)

    def test_timestamp_format(self):
        epoch = monotonic()
        log_time = self._handler._get_time_as_str(epoch)
        # make sure it has expected format
        utc_dt = datetime.strptime(log_time,
                                   '%Y-%m-%dT%H:%M:%S.%fZ')
        self.assertIsInstance(utc_dt, datetime)