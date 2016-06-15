from nio.util.logging.handlers.publisher.proxy import PublisherProxy
from nio.util.logging.handlers.publisher.tests.test_publisher \
    import TestPublisherBase


class TestPublisherNoCache(TestPublisherBase):

    def get_cache_interval(self):
        return 0

    def test_log_to_publisher_no_cache(self):
        """ Asserts that when interval is 0, no caching takes place
        """
        # wait for publisher to be ready
        self.assertTrue(PublisherProxy._publisher_ready_event.wait(1))

        msg1 = "warning message1 nocache"
        msg2 = "warning message2 nocache"
        warning_messages = [msg1, msg1, msg1, msg2]

        for message in warning_messages:
            self._publisher_logger.warning(message)

        self.assertIn(msg1, self._received_messages)
        self.assertIn(msg2, self._received_messages)
        self._received_messages.remove(msg1)
        self._received_messages.remove(msg2)

        # assert that msg1 was received the second time
        self.assertIn(msg1, self._received_messages)
        self._received_messages.remove(msg1)

        # assert that msg1 was received the third time
        self.assertIn(msg1, self._received_messages)
        self._received_messages.remove(msg1)

        # assert that msg1 was not received more than three times
        self.assertNotIn(msg1, self._received_messages)
        self.assertNotIn(msg2, self._received_messages)
