from unittest.mock import Mock

from nio.block.base import Block
from nio.block.context import BlockContext
from nio.block.terminals import DEFAULT_TERMINAL
from nio.router.base import BlockRouter
from nio.router.context import RouterContext
from nio.service.base import BlockExecution
from nio.signal.base import Signal
from nio.testing.test_case import NIOTestCase


class SenderBlock(Block):

    def __init__(self):
        super().__init__()
        self.id = self.__class__.__name__.lower()

    def process_signals(self, signals, input_id=DEFAULT_TERMINAL):
        self.notify_signals(signals)


class ReceiverBlock(Block):

    def __init__(self):
        super().__init__()
        self.id = self.__class__.__name__.lower()
        self.signal_cache = None

    def process_signals(self, signals, input_id=DEFAULT_TERMINAL):
        self.signal_cache = signals

    def reset_signals(self):
        self.signal_cache = None


class BlockExecutionTest(BlockExecution):

    def __init__(self, id, receivers):
        self.id = id
        self.receivers = receivers


class TestBaseDiagnostics(NIOTestCase):

    def test_diagnostics(self):
        """ Checking that router delivers signals and diagnostics """

        instance_id = "instance1"
        service_id = "service1"

        block_router = BlockRouter()
        context = BlockContext(block_router, dict())

        # create blocks
        sender_block = SenderBlock()
        sender_block.configure(context)
        receiver_block = ReceiverBlock()
        receiver_block.configure(context)

        # create context initialization data
        receiver_block_id = receiver_block.id()
        sender_block_id = sender_block.id()
        blocks = {receiver_block_id: receiver_block,
                  sender_block_id:sender_block}
        execution = [BlockExecutionTest(id=sender_block.id(),
                                        receivers=[receiver_block.id()])]

        signal_handler = Mock()
        router_context = RouterContext(execution, blocks,
                                       {
                                           "clone_signals": True,
                                           "diagnostics": True
                                       },
                                       mgmt_signal_handler=signal_handler,
                                       instance_id=instance_id,
                                       service_id=service_id)

        block_router.do_configure(router_context)
        block_router.do_start()

        common_attribute = "common attribute"
        common_value = "common value"
        signals = [Signal({common_attribute: common_value})]

        # make sure nothing has been delivered
        self.assertIsNone(receiver_block.signal_cache)

        self.assertEqual(
            len(block_router._diagnostic_manager._blocks_data), 0)
        sender_block.process_signals(signals)

        # make sure signals made it and diagnostic_manager.on_signal_delivery
        # was invoked
        self.assertIsNotNone(receiver_block.signal_cache)
        self.assertEqual(
            len(block_router._diagnostic_manager._blocks_data), 1)

        # make signal handler to be invoked
        block_router._diagnostic_manager._send_diagnostic()
        signal = signal_handler.call_args[0][0]
        self.assertEqual(signal.type, "RouterDiagnostic")
        self.assertEqual(signal.instance_id, instance_id)
        self.assertEqual(signal.service, service_id)
        self.assertEqual(len(signal.blocks_data), 1)
        block_data = signal.blocks_data[0]
        self.assertEqual(block_data["source_type"], sender_block.type())
        self.assertEqual(block_data["source"], sender_block.id())
        self.assertEqual(block_data["target_type"], receiver_block.type())
        self.assertEqual(block_data["target"], receiver_block.id())
        self.assertEqual(block_data["count"], 1)
        # assert data was cleared after a diagnostic delivery
        self.assertEqual(
            len(block_router._diagnostic_manager._blocks_data), 0)

        block_router.do_stop()

        # setup now a router without diagnostics
        router_context = RouterContext(execution, blocks,
                                       {
                                           "clone_signals": True,
                                           "diagnostics": False
                                       },
                                       mgmt_signal_handler=signal_handler)
        block_router.do_configure(router_context)
        block_router.do_start()
        receiver_block.reset_signals()
        sender_block.process_signals(signals)
        self.assertIsNotNone(receiver_block.signal_cache)
        # assert that diagnostics were not delivered
        self.assertEqual(
            len(block_router._diagnostic_manager._blocks_data), 0)

        block_router.do_stop()
