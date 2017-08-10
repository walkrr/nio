from unittest.mock import Mock

from nio.util.logging.handlers.publisher.cache import LogCache
from nio.testing.test_case import NIOTestCase
from nio.util.logging.handlers.publisher.tests import lineno, LogRecordTest, \
    get_log_record_same_line


class TestCache(NIOTestCase):

    def test_cache_different_lines(self):
        """ Asserts that records from different lines are cached """
        log_cache = LogCache(0.1)
        log_cache._cache.add = Mock()

        self.assertIsNotNone(log_cache._cache)
        self.assertEqual(log_cache._cache.add.call_count, 0)

        # when processing records from different lines,
        # message text is not relevant
        record1 = LogRecordTest(__file__, lineno(), "1")
        log_cache.process_record(record1)
        self.assertEqual(log_cache._cache.add.call_count, 1)

        record2 = LogRecordTest(__file__, lineno(), "1")
        log_cache.process_record(record2)
        self.assertEqual(log_cache._cache.add.call_count, 2)

    def test_cache_same_line_same_message(self):
        """ Asserts that only one record from same line is cached
        """
        log_cache = LogCache(0.1)

        record1 = get_log_record_same_line("1")
        record2 = get_log_record_same_line("1")

        # add a record without a mock so that it makes it to the cache
        log_cache.process_record(record1)

        # Mock adding to the cache, then add record2 and verify
        # that no call to add to the cache was made
        log_cache._cache.add = Mock()
        log_cache.process_record(record2)
        self.assertEqual(log_cache._cache.add.call_count, 0)

    def test_cache_same_line_diff_message(self):
        """ Asserts that records from same line are cached when msg differs """
        log_cache = LogCache(0.1)
        log_cache._cache.add = Mock()

        record1 = get_log_record_same_line("1")
        record2 = get_log_record_same_line("2")

        log_cache.process_record(record1)
        self.assertEqual(log_cache._cache.add.call_count, 1)

        log_cache.process_record(record2)
        self.assertEqual(log_cache._cache.add.call_count, 2)

    def test_cache_key_behavior(self):
        """ Asserts that record messages can be any object with a __str__ 
        implementation, which is always hashable
        """
        log_cache = LogCache(0.1)

        # two unhashable types for record.msg
        record1 = get_log_record_same_line({})
        record2 = get_log_record_same_line([])

        # process two dicts
        result1 = log_cache.process_record(record1)
        result2 = log_cache.process_record(record1)
        self.assertEqual(result1, False)
        self.assertEqual(result2, True)

        # process two lists
        result1 = log_cache.process_record(record2)
        result2 = log_cache.process_record(record2)
        self.assertEqual(result1, False)
        self.assertEqual(result2, True)
