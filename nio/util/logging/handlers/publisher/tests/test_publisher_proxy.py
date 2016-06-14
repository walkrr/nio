from nio import Signal
from nio.testing.test_case import NIOTestCase
from nio.util.logging.handlers.publisher.proxy import PublisherProxy, \
    PublisherNotReadyException


class TestPublisherProxy(NIOTestCase):

    def get_test_modules(self):
        return super().get_test_modules() | {'communication'}

    def test_publisher_create_failure(self):
        """ Asserts that signal does not get published when having a publisher
        waiting interval equal to 0
        """
        topics = {"type": "logging"}
        # set no waiting to be ready time
        max_publisher_ready_time = 0
        publisher_ready_wait_interval_time = 0.1

        PublisherProxy.init(topics,
                            max_publisher_ready_time,
                            publisher_ready_wait_interval_time)
        # can't publish signal since Publisher was not created
        with self.assertRaises(PublisherNotReadyException):
            PublisherProxy.publish([Signal()])
        PublisherProxy.close()

    def test_publisher_create_ok(self):
        """ Asserts that signal is published when having a publisher
        waiting interval
        """
        topics = {"type": "logging"}
        max_publisher_ready_time = 1
        publisher_ready_wait_interval_time = 0.1

        PublisherProxy.init(topics,
                            max_publisher_ready_time,
                            publisher_ready_wait_interval_time)
        PublisherProxy.publish([Signal()])
        PublisherProxy.close()
