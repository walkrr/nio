from unittest.mock import Mock, patch

from nio import Signal
from nio.block.base import Block
from nio.block.context import BlockContext
from nio.block.terminals import DEFAULT_TERMINAL
from nio.router.context import RouterContext
from nio.service.base import BlockExecution
from nio.testing.test_case import NIOTestCase
from nio.util.runner import RunnerStatus


class SenderBlock(Block):

    def __init__(self):
        super().__init__()
        self.id = self.__class__.__name__.lower()

    def process_signals(self, signals, input_id=DEFAULT_TERMINAL):
        self.notify_signals(signals)


class ExceptionThrowerReceiverBlock(Block):

    def __init__(self):
        super().__init__()
        self.id = self.__class__.__name__.lower()

    def process_signals(self, signals, input_id=DEFAULT_TERMINAL):
        raise RuntimeError("Throwing exception")


class BlockExecutionTest(BlockExecution):

    def __init__(self, id, receivers):
        self.id = id
        self.receivers = receivers


class TestThreadedRouter(NIOTestCase):

    def assert_router_process_signals_exception(self, block_router):

        context = BlockContext(block_router, dict())

        # create blocks
        sender_block = SenderBlock()
        sender_block.configure(context)
        receiver_block = ExceptionThrowerReceiverBlock()
        receiver_block.configure(context)

        # create context initialization data
        blocks = {
            receiver_block.id(): receiver_block,
            sender_block.id(): sender_block
        }
        execution = [BlockExecutionTest(id=sender_block.id(),
                                        receivers=[receiver_block.id()])]

        router_context = RouterContext(execution, blocks,
                                       {"check_signal_type": False})

        block_router.do_configure(router_context)
        block_router.do_start()
        self.assertEqual(block_router.status, RunnerStatus.started)

        # use this logger mock to assert later that an exception was logged
        logger_mock = Mock()
        with patch.object(block_router, "logger", new=logger_mock):
            self.assertFalse(logger_mock.exception.called)
            sender_block.process_signals(Signal({}))
            # assert that an exception was logged
            self.assertTrue(logger_mock.exception.called)

        # We should be able to safely send more signals - aka nothing died
        sender_block.process_signals(Signal({}))
        block_router.do_stop()

    def _router_in_status(self, router, status):
        return router.status.is_set(status)

    def test_base_router_process_signals_exception(self):
        """Checking that the thread pool executor version of the router logs
        process_signals exceptions and propagates exception to caller
        """

        from nio.router.base import BlockRouter
        block_router = BlockRouter()
        self.assert_router_process_signals_exception(block_router)

    def test_threaded_process_signals_exception(self):
        """Checking that the threaded version of the router logs
        process_signals exceptions but does not propagate exception to caller
        """

        from nio.router.threaded import ThreadedBlockRouter
        block_router = ThreadedBlockRouter()
        self.assert_router_process_signals_exception(block_router)

    def test_pool_thread_process_signals_exception(self):
        """Checking that the thread pool executor version of the router logs
        process_signals exceptions but does not propagate exception to caller
        """

        from nio.router.thread_pool_executor import ThreadedPoolExecutorRouter
        block_router = ThreadedPoolExecutorRouter()
        self.assert_router_process_signals_exception(block_router)
