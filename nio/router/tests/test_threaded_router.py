from threading import Event
from time import sleep

from nio.block.base import Block
from nio.block.context import BlockContext
from nio.block.terminals import DEFAULT_TERMINAL
from nio.router.context import RouterContext
from nio.service.base import BlockExecution
from nio.testing.condition import ensure_condition
from nio.testing.test_case import NIOTestCase


class SenderBlock(Block):

    def process_signals(self, signals):
        self.notify_signals(signals)


class ReceiverBlock(Block):

    def __init__(self):
        super().__init__()
        self.signal_received = Event()

    def process_signals(self, signals, input_id=DEFAULT_TERMINAL):
        # Wait half a second before setting the event
        # The calling thread should continue executing while this one is
        # sleeping
        sleep(0.5)
        self.signal_received.set()


class BlockExecutionTest(BlockExecution):

    def __init__(self, id, receivers):
        self.id = id
        self.receivers = receivers


class TestThreadedRouter(NIOTestCase):

    def test_threaded(self):
        """Checking that the threaded version of the router delivers signals"""

        from nio.router.threaded import ThreadedBlockRouter

        block_router = ThreadedBlockRouter()
        context = BlockContext(block_router, dict())

        # create blocks
        sender_block = SenderBlock()
        sender_block.configure(context)
        receiver_block = ReceiverBlock()
        receiver_block.configure(context)

        # create context initialization data
        blocks = {
            receiver_block.id():receiver_block,
            sender_block.id():sender_block
        }
        execution = [BlockExecutionTest(id=sender_block.id(),
                                        receivers=[receiver_block.id()])]

        router_context = RouterContext(execution, blocks,
                                       {"check_signal_type": False})

        block_router.do_configure(router_context)
        block_router.do_start()

        signals = [1, 2, 3, 4]

        # make sure nothing has been delivered
        self.assertFalse(receiver_block.signal_received.is_set())

        sender_block.process_signals(signals)
        # Asserting that signal has not been received, (since it would take
        # half a second for the event to be set, see above 'process_signals'
        # 'sleep' call) yet this thread has continued its execution
        self.assertFalse(receiver_block.signal_received.is_set())

        # Wait until signal is received
        ensure_condition(self._signal_is_received, receiver_block)
        self.assertTrue(receiver_block.signal_received.is_set())

        block_router.do_stop()

    def _signal_is_received(self, receiver_block):
        return receiver_block.signal_received.is_set()