from nio.util.logging.handlers.publisher.proxy import PublisherProxy
from nio.util.logging.handlers.publisher.tests.test_publisher \
    import TestPublisherBase


class TestPublisherCache(TestPublisherBase):

    def get_cache_interval(self):
        return 1

    def test_log_to_publisher_cache(self):
        """ Asserts that a CacheFilter can filter out repeated log messages """

        # wait for publisher to be ready
        self.assertTrue(PublisherProxy._publisher_ready_event.wait(1))

        msg1 = "warning message1 cached"
        msg2 = "warning message2 cached"
        warning_messages = [msg1, msg1, msg1, msg2]
        for message in warning_messages:
            self._publisher_logger.warning(message)

        # assert that msg1 and msg2 were received
        self.assertIn(msg1, self._received_messages)
        self.assertIn(msg2, self._received_messages)

        # remove 'once' received messages
        self._received_messages.remove(msg1)
        self._received_messages.remove(msg2)

        # assert that msg1 was received only once
        self.assertNotIn(msg1, self._received_messages)

        # assert that msg2 was received only once
        self.assertNotIn(msg2, self._received_messages)

        # reset received messages
        self._received_messages = []
        warning_messages = [msg1, msg2]
        # assert that both messages from same line make it
        for message in warning_messages:
            self._publisher_logger.warning(message)

        for message in warning_messages:
            self.assertIn(message, self._received_messages)
            # proof that no message was filtered
            self._received_messages.remove(message)

        # assert that after removing each message, not a single message remains
        self.assertEqual(len(self._received_messages), 0)
