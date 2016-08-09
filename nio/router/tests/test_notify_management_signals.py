from nio.util.runner import RunnerStatus
from nio.block.base import Block
from nio.router.base import BlockRouter
from nio.testing.test_case import NIOTestCaseNoModules
from nio.service.base import Service, BlockExecution
from nio.service.context import ServiceContext
from nio.signal.management import ManagementSignal
from nio.signal.base import Signal
from nio.signal.status import StatusSignal, BlockStatusSignal


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
           "properties": {'name': 'senderblock'}},
          {"type": ReceiverBlock,
           "properties": {'name': 'receiverblock'}},
          {"type": ReceiverBlock,
           "properties": {'name': 'notifierblock'}}]

execution = [BlockExecution()]
execution[0].name = "senderblock"
execution[0].receivers = ["receiverblock", "notifierblock"]

properties = {"name": "ServiceTestInstance",
              "auto_start": False,
              "execution": execution,
              "mappings": []}


class TestNotifyManagementSignals(NIOTestCaseNoModules):

    """ These tests mainly prove that the Service handles well the
    mappings specified and that the signals make it all the way through
    """

    def test_notify_status_change(self):
        """Test block statuses get updated on management signal notification"""
        context = ServiceContext(properties, blocks, BlockRouter)
        service = Service()
        service.do_configure(context)
        self.assertEqual(service._blocks['notifierblock'].status,
                         RunnerStatus.configured)
        service.do_start()

        error_signal = BlockStatusSignal(RunnerStatus.error, 'It just broke...')
        notifier_block = service._blocks['notifierblock']
        notifier_block.notify_management_signal(error_signal)

        self.assertTrue(service._blocks['notifierblock']._status.
                        is_set(RunnerStatus.error))
        service.do_stop()

    def test_bad_signals_no_effect(self):
        """Test nothing happens when non management signals are notified"""
        context = ServiceContext(properties, blocks, BlockRouter)
        service = Service()
        service.do_configure(context)
        service.do_start()

        signal = ManagementSignal()
        notifier_block = service._blocks['notifierblock']
        notifier_block.notify_management_signal(signal)

        self.assertEqual(service._blocks['notifierblock'].status,
                         RunnerStatus.started)

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

        error_signal = BlockStatusSignal(RunnerStatus.error, 'Broken')
        notifier_block = service._blocks['notifierblock']
        notifier_block.notify_management_signal(error_signal)
        self.assertTrue(service._blocks['notifierblock']._status.
                        is_set(RunnerStatus.error))

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
