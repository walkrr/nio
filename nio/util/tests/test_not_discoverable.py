from nio.testing.test_case import NIOTestCaseNoModules
from nio.util.discovery import not_discoverable, is_class_not_discoverable
from nio.block.base import Block


@not_discoverable
class NotDiscoverableBlock(Block):
    pass


class DiscoverableSubBlock(NotDiscoverableBlock):
    pass


@not_discoverable
class NotDiscoverableSubBlock(NotDiscoverableBlock):
    pass


class TestDiscoverable(NIOTestCaseNoModules):

    def test_not_discoverable(self):
        """Tests not discoverable attribute"""
        self.assertTrue(is_class_not_discoverable(NotDiscoverableBlock))
        self.assertFalse(is_class_not_discoverable(DiscoverableSubBlock))
        self.assertTrue(is_class_not_discoverable(NotDiscoverableSubBlock))
