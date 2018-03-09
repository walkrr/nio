from threading import Event
from unittest.mock import Mock

from nio.router.context import RouterContext
from nio.router.diagnostic import DiagnosticManager
from nio.signal.management import ManagementSignal
from nio.testing.condition import ConditionWaiter
from nio.testing.test_case import NIOTestCase


class TestDiagnostic(NIOTestCase):

    def test_diagnostic(self):

        def check_handler_was_called(signal_handler):
            return signal_handler.call_count > 0

        instance_id1 = "instance_id1"
        service1 = "service1"
        source_type = "source_type"
        source1 = "source1"
        target_type = "target_type"
        target1 = "target1"
        count11 = 5
        count12 = 8

        target2 = "target2"
        count2 = 4

        signal_handler = Mock()
        router_context = RouterContext([], {},
                                       {
                                           "diagnostic_interval": 0.1
                                       },
                                       mgmt_signal_handler=signal_handler,
                                       instance_id=instance_id1,
                                       service_id=service1)

        dm = DiagnosticManager()
        dm.do_configure(router_context)
        dm.do_start()

        event = Event()
        condition = ConditionWaiter(event,
                                    check_handler_was_called,
                                    signal_handler)
        condition.start()
        dm.on_signal_delivery(source_type, source1,
                              target_type, target1, count11)
        dm.on_signal_delivery(source_type, source1,
                              target_type, target1, count12)
        dm.on_signal_delivery(source_type, source1,
                              target_type, target2, count2)
        self.assertTrue(event.wait(1))
        condition.stop()

        self.assertEqual(signal_handler.call_count, 1)
        signal = signal_handler.call_args[0][0]
        self.assertIsInstance(signal, ManagementSignal)
        # assert signal fields
        self.assertEqual(signal.type, "RouterDiagnostic")
        self.assertEqual(signal.instance_id, instance_id1)
        self.assertEqual(signal.service, service1)
        self.assertLessEqual(signal.start_time, signal.end_time)
        for block_data in signal.blocks_data:
            self.assertEqual(block_data["source_type"], source_type)
            self.assertEqual(block_data["target_type"], target_type)
            self.assertEqual(block_data["source"], source1)
            if block_data["target"] == target1:
                # assert that count was added up
                self.assertEqual(block_data["count"], count11 + count12)
            elif block_data["target"] == target2:
                self.assertEqual(block_data["count"], count2)
            else:
                raise ValueError("Invalid target")

        dm.do_stop()

    def test_times(self):
        """ Assert diagnostic start_time/end_time values.
        """
        instance_id1 = "instance_id1"
        service1 = "service1"
        source_type = "source_type"
        source1 = "source1"
        target_type = "target_type"
        target1 = "target1"
        count1 = 5

        signal_handler = Mock()
        router_context = RouterContext([], {},
                                       {},
                                       mgmt_signal_handler=signal_handler,
                                       instance_id=instance_id1,
                                       service_id=service1)

        dm = DiagnosticManager()
        dm.do_configure(router_context)
        dm.do_start()

        dm.on_signal_delivery(source_type, source1,
                              target_type, target1, count1)
        dm._send_diagnostic()
        self.assertEqual(signal_handler.call_count, 1)
        signal1 = signal_handler.call_args[0][0]

        # cause a second diagnostic
        signal_handler.reset_mock()
        dm.on_signal_delivery(source_type, source1,
                              target_type, target1, count1)
        dm._send_diagnostic()
        self.assertEqual(signal_handler.call_count, 1)
        signal2 = signal_handler.call_args[0][0]

        # assert start_time and end_time combinations
        self.assertLessEqual(signal1.start_time, signal1.end_time)
        self.assertEqual(signal1.end_time, signal2.start_time)
        self.assertLessEqual(signal2.start_time, signal2.end_time)

        dm.do_stop()
