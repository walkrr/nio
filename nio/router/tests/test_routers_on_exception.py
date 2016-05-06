from time import sleep
from unittest.mock import Mock, patch

from nio import Signal
from nio.block.base import Block
from nio.block.context import BlockContext
from nio.block.terminals import DEFAULT_TERMINAL
from nio.service.base import BlockExecution
from nio.router.context import RouterContext
from nio.testing.test_case import NIOTestCase
from nio.util.runner import RunnerStatus


class SenderBlock(Block):

    def __init__(self):
        super().__init__()
        self.name = self.__class__.__name__.lower()

    def process_signals(self, signals, input_id=DEFAULT_TERMINAL):
        self.notify_signals(signals)


class ExceptionThrowerReceiverBlock(Block):

    def __init__(self):
        super().__init__()
        self.name = self.__class__.__name__.lower()

    def process_signals(self, signals, input_id=DEFAULT_TERMINAL):
        raise RuntimeError("Throwing exception")


class BlockExecutionTest(BlockExecution):

    def __init__(self, name, receivers):
        self.name = name
        self.receivers = receivers


class TestThreadedRouter(NIOTestCase):

    def assert_router_process_signals_exception(self, block_router,
                                                catch_exception):

        context = BlockContext(block_router, dict())

        # create blocks
        sender_block = SenderBlock()
        sender_block.configure(context)
        receiver_block = ExceptionThrowerReceiverBlock()
        receiver_block.configure(context)

        # create context initialization data
        blocks = dict(receiverblock=receiver_block,
                      senderblock=sender_block)
        execution = [BlockExecutionTest(name="senderblock",
                                        receivers=["receiverblock"])]

        router_context = RouterContext(execution, blocks,
                                       {"check_signal_type": False})

        block_router.do_configure(router_context)
        block_router.do_start()
        self.assertEqual(block_router.status, RunnerStatus.started)

        # use this logger mock to assert later that an exception was logged
        logger_mock = Mock()
        with patch.object(block_router, "logger", new=logger_mock):
            self.assertFalse(logger_mock.exception.called)
            if catch_exception:
                # asserts that propagates the exception
                with self.assertRaises(RuntimeError):
                    sender_block.process_signals(Signal({}))
            else:
                sender_block.process_signals(Signal({}))

            # asynchronous routers need time to process signals
            sleep(0.1)
            # assert that router status changed and an exception was logged
            self.assertTrue(block_router.status.is_set(RunnerStatus.error))
            self.assertTrue(logger_mock.exception.called)

        block_router.do_stop()

    def test_base_router_process_signals_exception(self):
        """Checking that the thread pool executor version of the router logs
        process_signals exceptions and propagates exception to caller
        """

        from nio.router.base import BlockRouter
        block_router = BlockRouter()
        self.assert_router_process_signals_exception(block_router, True)

    def test_threaded_process_signals_exception(self):
        """Checking that the threaded version of the router logs
        process_signals exceptions but does not propagate exception to caller
        """

        from nio.router.threaded import ThreadedBlockRouter
        block_router = ThreadedBlockRouter()
        self.assert_router_process_signals_exception(block_router, False)

    def test_pool_thread_process_signals_exception(self):
        """Checking that the thread pool executor version of the router logs
        process_signals exceptions but does not propagate exception to caller
        """

        from nio.router.thread_pool_executor import ThreadedPoolExecutorRouter
        block_router = ThreadedPoolExecutorRouter()
        self.assert_router_process_signals_exception(block_router, False)
