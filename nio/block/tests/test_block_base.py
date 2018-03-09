from unittest.mock import patch, Mock

from nio.block.base import Block
from nio.block.context import BlockContext
from nio.block.generator_block import GeneratorBlock
from nio.block.terminals import DEFAULT_TERMINAL
from nio.block.terminator_block import TerminatorBlock
from nio.properties.exceptions import AllowNoneViolation
from nio.router.base import BlockRouter
from nio.router.context import RouterContext
from nio.signal.base import Signal
from nio.signal.status import BlockStatusSignal
from nio.testing.test_case import NIOTestCaseNoModules
from nio.util.runner import RunnerStatus


class TestBaseBlock(NIOTestCaseNoModules):

    def test_configure(self):
        """Make sure a block can be configured"""
        blk = Block()
        blk.configure(BlockContext(
            BlockRouter(),
            {"id": "BlockId", "log_level": "WARNING"}))
        # Make sure the name property got set properly
        self.assertEqual(blk.id(), "BlockId")

    def test_invalid_configure(self):
        """Make sure a block is configured with valid information"""
        class JustAnObject(object):
            pass
        with self.assertRaises(TypeError):
            # Can't configure with a non BlockContext
            Block().configure(JustAnObject)
        with self.assertRaises(TypeError):
            # The context's block router needs to be a BlockRouter
            Block().configure(BlockContext(JustAnObject, {}))
        with self.assertRaises(AllowNoneViolation):
            # Block needs an id
            Block().configure(BlockContext(BlockRouter(), {"id": None}))
        with self.assertRaises(TypeError):
            # Wrong types (like log_level not being correct) raise TypeError
            Block().configure(BlockContext(BlockRouter(), {"id": "BlockId",
                                                           "log_level": 42}))

    def test_notify_management_signal(self):
        """Test the block can notify management signals properly to router """
        blk = Block()
        blk.configure(BlockContext(
            BlockRouter(),
            {"id": "BlockId", "log_level": "WARNING"}))
        my_sig = Signal({"key": "val"})
        with patch.object(blk, '_block_router') as router_patch:
            blk.notify_management_signal(my_sig)
            router_patch.notify_management_signal.assert_called_once_with(
                blk, my_sig)

    def test_service_notify_management_signal(self):
        """ Test the block can notify management signals to the service """
        blk = Block()
        service_mgmt_signal_handler = Mock()
        block_router = BlockRouter()
        router_context = \
            RouterContext([], {},
                          mgmt_signal_handler=service_mgmt_signal_handler)
        block_router.configure(router_context)
        blk.configure(BlockContext(
            block_router,
            {"id": "BlockId", "log_level": "WARNING"}))
        my_sig = Signal({"key": "val"})
        blk.notify_management_signal(my_sig)
        service_mgmt_signal_handler.assert_called_once_with(my_sig)

    def test_notify_signals(self):
        """Test the block can notify signals properly"""
        blk = Block()
        block_id = 'block1'
        service_id = 'service1'
        blk.configure(BlockContext(
            BlockRouter(),
            {"id": block_id},
            service_id=service_id))

        my_sigs = [Signal({"key": "val"})]
        with patch.object(blk, '_block_router') as router_patch:
            blk.notify_signals(my_sigs)
            router_patch.notify_signals.assert_called_once_with(
                blk, my_sigs, None)

        # test sending more than one Signal
        with patch.object(blk, '_block_router') as router_patch:
            signals = [Signal(), Signal()]
            blk.notify_signals(signals, "default")
            router_patch.notify_signals.assert_called_once_with(
                blk, signals, "default")

        # test that sending signals as a set is allowed
        with patch.object(blk, '_block_router') as router_patch:
            signals = set()
            signals.add(Signal())
            signals.add(Signal())
            blk.notify_signals(signals, "default")
            router_patch.notify_signals.assert_called_once_with(
                blk, signals, "default")

        # test that a Signal as a non-iterable is accepted and
        # propagated as a list
        with patch.object(blk, '_block_router') as router_patch:
            single_signal = Signal()
            blk.notify_signals(single_signal, "default")
            router_patch.notify_signals.assert_called_once_with(
                blk, [single_signal], "default")

        # test that a dictionary, empty or not, is not accepted and
        # TypeError is raised
        dict_signal = {}
        with self.assertRaises(TypeError):
            blk.notify_signals(dict_signal, "default")

        dict_signal = {"key": "val"}
        with self.assertRaises(TypeError):
            blk.notify_signals(dict_signal, "default")

    def test_import_locations(self):
        """Make sure the block can be imported from the nio root"""
        from nio import Block as nioBlock
        self.assertEqual(nioBlock, Block)

    def test_block_properties(self):
        """Make sure the block's properties contains common properties"""
        blk = Block()
        props = blk.properties()
        self.assertIn('type', props)
        self.assertIn('log_level', props)
        self.assertIn('name', props)

    def test_block_description(self):
        """Make sure the block's description contains common properties"""
        desc = Block.get_description()
        self.assertIn('type', desc['properties'])
        self.assertIn('log_level', desc['properties'])
        self.assertIn('name', desc['properties'])
        self.assertIn('properties', desc['commands'])

    def test_default_block_terminals(self):
        """Make sure the block has its default terminals"""
        blk = Block()
        self.assertTrue(blk.is_input_valid(DEFAULT_TERMINAL))
        self.assertTrue(blk.is_output_valid(DEFAULT_TERMINAL))
        self.assertFalse(blk.is_input_valid('fake input'))
        self.assertFalse(blk.is_output_valid('fake output'))

    def test_terminal_block_terminals(self):
        """Make sure the block has only an input terminal"""
        blk = TerminatorBlock()
        self.assertTrue(blk.is_input_valid(DEFAULT_TERMINAL))
        self.assertFalse(blk.is_output_valid(DEFAULT_TERMINAL))

    def test_generator_block_terminals(self):
        """Make sure the block has only an output terminal"""
        blk = GeneratorBlock()
        self.assertFalse(blk.is_input_valid(DEFAULT_TERMINAL))
        self.assertTrue(blk.is_output_valid(DEFAULT_TERMINAL))

    def test_populate_block_status_signal(self):
        blk = Block()

        block_name = 'block1'
        service_id = 'service1'
        blk.configure(BlockContext(
            BlockRouter(),
            {"id": "block_id",
             "name": block_name},
            service_id=service_id))

        warning = BlockStatusSignal(
                    RunnerStatus.warning, message='It just broke...')
        self.assertIsNone(warning.service_id)
        self.assertIsNone(warning.block_name)
        blk.notify_management_signal(warning)
        self.assertIsNotNone(warning.service_id)
        self.assertIsNotNone(warning.block_name)
        self.assertEqual(warning.service_id, service_id)
        self.assertEqual(warning.block_name, block_name)
