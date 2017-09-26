from collections import defaultdict
from datetime import timedelta
from threading import RLock

from nio.modules.scheduler.job import Job
from nio.signal.management import ManagementSignal
from nio.util.runner import Runner


class DiagnosticManager(Runner):

    def __init__(self):
        super().__init__()

        self._instance_id = None
        self._interval = None
        self._mgmt_signal_handler = None
        self._job = None

        self._signals_lock = RLock()
        self._signals = None

    def configure(self, context):
        self._instance_id = context.instance_id
        self._interval = \
            context.settings.get("diagnostic_interval", 60)
        self._mgmt_signal_handler = context.mgmt_signal_handler
        self._signals = \
            defaultdict(lambda:
                        defaultdict(lambda:
                                    defaultdict((int))))

    def start(self):
        super().start()

        # create job to periodically send updates
        if self._interval > 0:
            self._job = \
                Job(self._send_diagnostic,
                    timedelta(seconds=self._interval),
                    True)

    def stop(self):
        if self._job:
            self._job.cancel()

        # Send what we have saved
        self._send_diagnostic()
        super().stop()

    def on_signal_delivery(self, service, source, target, count):
        with self._signals_lock:
            self._signals[service][source][target] += count

    def _send_diagnostic(self):
        with self._signals_lock:
            if self._signals and self._mgmt_signal_handler:
                signals_to_send = []
                for service, data in self._signals.items():
                    for source, target_data in data.items():
                        for target, count in target_data.items():
                            signals_to_send.append(
                                ManagementSignal(
                                    {
                                        "type": "RouterDiagnostic",
                                        "instance_id": self._instance_id,
                                        "service": service,
                                        "source": source,
                                        "target": target,
                                        "count": count
                                    }
                                )
                            )

                self._mgmt_signal_handler(signals_to_send)
                self._signals.clear()
