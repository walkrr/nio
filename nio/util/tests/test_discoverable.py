from nio.testing.test_case import NIOTestCaseNoModules
from nio.util.discovery import discoverable, not_discoverable, \
    is_class_discoverable
from nio.block.base import Block


@discoverable
class DiscoverableBlock(Block):
    pass


class NotSpecifiedSubBlock(DiscoverableBlock):
    pass


@discoverable
class DiscoverableSubBlock(NotSpecifiedSubBlock):
    pass


@not_discoverable
class NotDiscoverableBlock(Block):
    pass


@not_discoverable
class NotDiscoverableSubBlock(Block):
    pass


@not_discoverable
class NotDiscoverableInheritingBlock(DiscoverableBlock):
    pass


@discoverable
class DiscoverableInheritingBlock(NotDiscoverableBlock):
    pass


class TestDiscoverable(NIOTestCaseNoModules):

    def test_is_class_discoverable(self):

        # asserting simple discoverable and not_discoverable decorators
        self.assertTrue(is_class_discoverable(DiscoverableBlock))
        self.assertFalse(is_class_discoverable(NotDiscoverableBlock))
        # assert discoverability does not come from default discoverability
        self.assertTrue(is_class_discoverable(DiscoverableBlock, False))
        self.assertFalse(is_class_discoverable(NotDiscoverableBlock, True))

        # assert default discoverability when not provided
        self.assertFalse(is_class_discoverable(NotSpecifiedSubBlock))

        # show that a non-specified block would go either way depending on
        # the default discoverability setting
        self.assertTrue(is_class_discoverable(NotSpecifiedSubBlock, True))
        self.assertFalse(is_class_discoverable(NotSpecifiedSubBlock, False))

        # assert straightforward inheriting blocks specifying own decorators
        self.assertTrue(is_class_discoverable(DiscoverableSubBlock))
        self.assertFalse(is_class_discoverable(NotDiscoverableSubBlock))
        # assert discoverability does not come from default discoverability
        self.assertTrue(is_class_discoverable(DiscoverableSubBlock, False))
        self.assertFalse(is_class_discoverable(NotDiscoverableSubBlock, True))

        # as expected a block specifying opposite-to-parent discoverability
        # overrides
        self.assertTrue(is_class_discoverable(DiscoverableInheritingBlock))
        self.assertFalse(is_class_discoverable(NotDiscoverableInheritingBlock))
