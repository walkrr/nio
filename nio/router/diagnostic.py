from collections import defaultdict
from datetime import timedelta, datetime
from threading import RLock

from nio.modules.scheduler.job import Job
from nio.signal.management import ManagementSignal
from nio.util.runner import Runner


class DiagnosticManager(Runner):

    def __init__(self):
        super().__init__()

        self._start_time = None
        self._instance_id = None
        self._service_name = None
        self._interval = None
        self._mgmt_signal_handler = None
        self._job = None

        self._blocks_data_lock = RLock()
        self._blocks_data = None

    def configure(self, context):
        self._instance_id = context.instance_id
        self._service_name = context.service_name
        self._interval = \
            context.settings.get("diagnostic_interval", 60)
        self._mgmt_signal_handler = context.mgmt_signal_handler
        self._blocks_data = defaultdict(lambda: defaultdict(int))

    def start(self):
        super().start()

        # initialize collection start time
        self._start_time = datetime.utcnow().timestamp()
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

    def on_signal_delivery(self, source, target, count):
        with self._blocks_data_lock:
            self._blocks_data[source][target] += count

    def _send_diagnostic(self):
        with self._blocks_data_lock:
            end_time = datetime.utcnow().timestamp()
            if self._blocks_data and self._mgmt_signal_handler:
                blocks_data = []
                for source, target_data in self._blocks_data.items():
                    for target, count in target_data.items():
                        blocks_data.append(
                            {
                                "source": source,
                                "target": target,
                                "count": count
                            }
                        )
                self._mgmt_signal_handler(
                    ManagementSignal(
                        {
                            "type": "RouterDiagnostic",
                            "instance_id": self._instance_id,
                            "service": self._service_name,
                            "blocks_data": blocks_data,
                            "start_time": self._start_time,
                            "end_time": end_time
                        }
                    )
                )
                self._blocks_data.clear()
            self._start_time = end_time
