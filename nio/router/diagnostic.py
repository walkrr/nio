from datetime import timedelta
from threading import RLock

from nio.modules.scheduler.job import Job
from nio.util.runner import Runner


class DiagnosticManager(Runner):

    def __init__(self):
        super().__init__()

        self._interval = None
        self._mgmt_signal_handler = None
        self._job = None

        self._signals_lock = RLock()
        self._signals = []

    def configure(self, context):
        self._interval = \
            context.settings.get("diagnostic_interval", 30)
        self._mgmt_signal_handler = context.mgmt_signal_handler

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

    def on_signal(self, signal):
        with self._signals_lock:
            self._signals.append(signal)

    def _send_diagnostic(self):
        with self._signals_lock:
            if self._signals:
                self._mgmt_signal_handler(self._signals)
                self._signals.clear()
