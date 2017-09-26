from threading import Event
from unittest.mock import Mock

from nio.router.context import RouterContext
from nio.router.diagnostic import DiagnosticManager
from nio.signal.management import ManagementSignal
from nio.testing.condition import ConditionWaiter
from nio.testing.test_case import NIOTestCase


class TestDiagnostic(NIOTestCase):

    def test_diagnostic(self):
        instance_id1 = "instance_id1"
        service1 = "service1"
        source1 = "source1"
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
                                       instance_id=instance_id1)


        dm = DiagnosticManager()
        dm.do_configure(router_context)
        dm.do_start()

        event = Event()
        condition = ConditionWaiter(event,
                                    self._check_handler_was_called,
                                    signal_handler)
        condition.start()
        dm.on_signal_delivery(service1, source1, target1, count11)
        dm.on_signal_delivery(service1, source1, target1, count12)
        dm.on_signal_delivery(service1, source1, target2, count2)
        self.assertTrue(event.wait(1))
        condition.stop()

        self.assertEqual(signal_handler.call_count, 1)
        self.assertEqual(len(signal_handler.call_args[0][0]), 2)
        for signal in signal_handler.call_args[0][0]:
            self.assertIsInstance(signal, ManagementSignal)
            # assert signal fields
            self.assertEqual(signal.type, "RouterDiagnostic")
            self.assertEqual(signal.instance_id, instance_id1)
            self.assertEqual(signal.service, service1)
            self.assertEqual(signal.source, source1)
            if signal.target == target1:
                # assert that count was added up
                self.assertEqual(signal.count, count11 + count12)
            elif signal.target == target2:
                # assert that count was added up
                self.assertEqual(signal.count, count2)
            else:
                raise ValueError("Invalid target")

        dm.do_stop()

    def _check_handler_was_called(self, signal_handler):
        return signal_handler.call_count > 0
