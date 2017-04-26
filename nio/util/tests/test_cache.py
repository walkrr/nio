from time import time

from nio.testing.condition import ensure_condition
from nio.testing.test_case import NIOTestCase
from nio.util.cache import Cache
from nio.util.threading import spawn


class TestCache(NIOTestCase):

    def _item_get(self, cache, key, result):
        return cache.get(key) == result

    def test_add(self):
        """ Adding an item that overrides duration """

        cache_duration = 5
        cache = Cache(cache_duration)
        key = 1
        item = "1"
        self.assertIsNone(cache.get(key))

        override_duration = 0.1
        t1 = time()
        cache.add(key, item, duration=override_duration)
        self.assertEqual(cache.get(key), item)

        ensure_condition(self._item_get, cache, key, None)
        t2 = time()
        self.assertGreaterEqual(t2, t1+override_duration)
        self.assertLess(t2, t1+cache_duration)
        self.assertIsNone(cache.get(key))

    def test_duration_not_specified(self):
        """ Adding an item that does not specifies duration """
        cache_duration = 0.1
        cache = Cache(cache_duration)

        key = 1
        item = "1"
        self.assertIsNone(cache.get(key))
        t1 = time()
        cache.add(key, item)
        self.assertEqual(cache.get(key), item)
        ensure_condition(self._item_get, cache, key, None)
        t2 = time()
        self.assertGreaterEqual(t2, t1+cache_duration)
        self.assertIsNone(cache.get(key))

    def test_no_duration(self):
        """ Verifies that when duration is 0 nothing gets added """
        cache = Cache(0)

        key = 1
        item = "1"
        self.assertIsNone(cache.get(key))
        cache.add(key, item)
        self.assertIsNone(cache.get(key))

    def test_item_with_zero_duration(self):
        """ Verifies that when the item is added with 0 duration nothing added

        (default duration does not apply)
        """

        cache = Cache(2)

        key = 1
        item = "1"
        self.assertIsNone(cache.get(key))
        cache.add(key, item, 0)
        self.assertIsNone(cache.get(key))

    def test_default_when_item_is_missing(self):
        """ Verifies that when item does not exist the default is returned """

        cache = Cache(2)
        self.assertEqual(cache.get("not existant", "default to be retrieved"),
                         "default to be retrieved")

    def _length_equals(self, item, value):
        return len(item) == value

    def test_multithreading(self):
        """ Verifies that adding from multiple threads keeps results as expected
        """
        cache_duration = 0.2
        t1 = time()
        num_threads = 20
        cache = Cache(cache_duration)
        for i in range(num_threads):
            spawn(cache.add, "key{0}".format(i), i)
        ensure_condition(self._length_equals, cache._cache, num_threads)
        # assert all items are in cache, and with the right values
        self.assertEqual(len(cache._cache), num_threads)
        for i in range(num_threads):
            self.assertEqual(cache.get("key{0}".format(i)), i)
        # assert all items expired
        ensure_condition(self._length_equals, cache._cache, 0)
        self.assertGreaterEqual(time(), t1+cache_duration)
        self.assertEqual(len(cache._cache), 0)

    def test_adding_same_key(self):
        """ Make sure item for a given key can be overriden before it expires
        """
        cache = Cache(0.4)

        key = 1
        item = "1"
        cache.add(key, item)
        self.assertEqual(cache.get(key), item)
        item = "2"
        cache.add(key, item)
        self.assertEqual(cache.get(key), item)
        self.assertEqual(len(cache._cache), 1)
