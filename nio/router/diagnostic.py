from collections import defaultdict
from datetime import timedelta, datetime
from threading import RLock

from nio.modules.scheduler.job import Job
from nio.signal.management import ManagementSignal
from nio.util.runner import Runner


class DiagnosticManager(Runner):

    _type_separator = "###"

    def __init__(self):
        super().__init__()

        self._start_time = None
        self._instance_id = None
        self._service_id = None
        self._service_name = None
        self._interval = None
        self._mgmt_signal_handler = None
        self._job = None

        self._blocks_data_lock = RLock()
        self._blocks_data = None

    def configure(self, context):
        self._instance_id = context.instance_id
        self._service_id = context.service_id
        self._service_name = context.service_name
        self._interval = \
            context.settings.get("diagnostic_interval", 3600)
        self._mgmt_signal_handler = context.mgmt_signal_handler
        self._blocks_data = defaultdict(lambda: defaultdict(int))

    def start(self):
        super().start()

        # initialize collection start time
        self._start_time = self._create_timestamp()
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

    def on_signal_delivery(self,
                           source_type, source,
                           target_type, target, count):
        with self._blocks_data_lock:
            source_key = self._create_key(source_type, source)
            target_key = self._create_key(target_type, target)
            self._blocks_data[source_key][target_key] += count

    def _send_diagnostic(self):
        with self._blocks_data_lock:
            end_time = self._create_timestamp()
            if self._blocks_data and self._mgmt_signal_handler:
                blocks_data = []
                for source_key, target_data in self._blocks_data.items():
                    for target_key, count in target_data.items():
                        source_type, source = \
                            self._split_key(source_key)
                        target_type, target = \
                            self._split_key(target_key)
                        blocks_data.append(
                            {
                                "source_type": source_type,
                                "source": source,
                                "target_type": target_type,
                                "target": target,
                                "count": count
                            }
                        )
                self._mgmt_signal_handler(
                    ManagementSignal(
                        {
                            "type": "RouterDiagnostic",
                            "instance_id": self._instance_id,
                            "service_id": self._service_id,
                            "service": self._service_name,
                            "blocks_data": blocks_data,
                            "start_time": self._start_time,
                            "end_time": end_time
                        }
                    )
                )
                self._blocks_data.clear()
            self._start_time = end_time

    @staticmethod
    def _create_timestamp():
        """ Creates a calculated UTC timestamp.

        This is needed because datetime.utcnow().timestamp() does not
        play nice with timezones, so we calculate it manually.

        Returns:
            timestamp
        """
        return (datetime.utcnow() - datetime(1970,1,1)).total_seconds()

    @staticmethod
    def _create_key(_type, name):
        """ Creates a key by merging type and name

        Returns:
            created key
        """
        return "{}{}{}".format(_type, DiagnosticManager._type_separator, name)

    @staticmethod
    def _split_key(_id):
        """ Splits a key

        Returns:
            type, name tuple
        """
        ids = _id.split(DiagnosticManager._type_separator)
        return ids[0], ids[1]
