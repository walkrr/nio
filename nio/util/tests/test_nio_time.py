from nio.testing.test_case import NIOTestCase

from datetime import datetime
from nio.util.nio_time import get_nio_time


class TestNioTime(NIOTestCase):

    def test_nio_time(self):
        # asserts nio ISO 8601 time format
        nio_time = get_nio_time()
        # make sure it has expected format
        utc_dt = datetime.strptime(nio_time,
                                   '%Y-%m-%dT%H:%M:%S.%fZ')
        self.assertIsInstance(utc_dt, datetime)
