from nio.block.base import Block
from nio.router.base import BlockRouter
from nio.service.base import Service, BlockExecution
from nio.service.context import ServiceContext
from nio.signal.base import Signal
from nio.signal.management import ManagementSignal
from nio.signal.status import StatusSignal, BlockStatusSignal
from nio.testing.test_case import NIOTestCase
from nio.util.runner import RunnerStatus


class SenderBlock(Block):

    def __init__(self):
        super().__init__()

    def process_signals(self, signals, input_id='default'):
        self.notify_signals(signals)


class ReceiverBlock(Block):

    def __init__(self):
        super().__init__()
        # Keep track of how many signals we have processed
        self.signals_processed = 0

    def process_signals(self, signals, input_id='default'):
        self.signals_processed += len(signals)


# We have one sender block sending to two receiver blocks.
# In some of the tests, one of the recevier blocks (the notifier) will notify
# some management signals to the router
blocks = [{"type": SenderBlock,
           "properties": {'id': 'senderblock'}},
          {"type": ReceiverBlock,
           "properties": {'id': 'receiverblock'}},
          {"type": ReceiverBlock,
           "properties": {'id': 'notifierblock'}}]

execution = [BlockExecution()]
execution[0].id = "senderblock"
execution[0].receivers = ["receiverblock", "notifierblock"]

properties = {"id": "ServiceTestInstance",
              "auto_start": False,
              "execution": execution,
              "mappings": []}


class TestNotifyManagementSignals(NIOTestCase):

    """ These tests mainly prove that the Service handles well the
    mappings specified and that the signals make it all the way through
    """

    def test_non_management_signals_no_effect(self):
        """Test nothing happens when non management signals are notified"""
        context = ServiceContext(properties, blocks, BlockRouter)
        service = Service()
        service.do_configure(context)
        service.do_start()

        # Notifying a base management signal won't change the status of
        # the block
        signal = ManagementSignal()
        notifier_block = service._blocks['notifierblock']
        notifier_block.notify_management_signal(signal)
        self.assertEqual(service._blocks['notifierblock'].status,
                         RunnerStatus.started)

        # Notifying a regular signal also won't change the status of
        # the block
        signal2 = Signal()
        notifier_block.notify_management_signal(signal2)
        self.assertEqual(service._blocks['notifierblock'].status,
                         RunnerStatus.started)

        service.do_stop()

    def test_skip_error_status_blocks(self):
        """Test that signals aren't delivered to blocks in error state"""
        context = ServiceContext(properties, blocks, BlockRouter)
        service = Service()
        service.do_configure(context)
        service.do_start()

        signals = [Signal({"1": 1}),
                   Signal({"2": 2}),
                   Signal({"3": 3}),
                   Signal({"4": 4})]

        service._blocks['senderblock'].process_signals(signals)

        self.assertEqual(service._blocks['receiverblock'].signals_processed, 4)
        self.assertEqual(service._blocks['notifierblock'].signals_processed, 4)

        notifier_block = service._blocks['notifierblock']
        notifier_block.status.add(RunnerStatus.error)

        service._blocks['senderblock'].process_signals(signals)

        # We expect our non-error block to get the next 4 signals,
        # but our error status block (the notifier) will not
        self.assertEqual(service._blocks['receiverblock'].signals_processed, 8)
        self.assertEqual(service._blocks['notifierblock'].signals_processed, 4)

        service.do_stop()

    def test_notify_with_warning(self):
        """Test that signals are still delivered to block's in warning"""
        context = ServiceContext(properties, blocks, BlockRouter)
        service = Service()
        service.do_configure(context)

        service.do_start()

        warning = StatusSignal(RunnerStatus.warning, 'Maybe broken?')
        notifier_block = service._blocks['notifierblock']
        notifier_block.notify_management_signal(warning)

        signals = [Signal({"1": 1}),
                   Signal({"2": 2}),
                   Signal({"3": 3}),
                   Signal({"4": 4})]

        service._blocks['senderblock'].process_signals(signals)
        self.assertEqual(service._blocks['receiverblock'].signals_processed, 4)
        self.assertEqual(service._blocks['notifierblock'].signals_processed, 4)
        service.do_stop()
