from threading import RLock, Event
from time import sleep
from datetime import datetime, timedelta

from nio.modules.communication.publisher import Publisher
from nio.modules.module import ModuleNotInitialized
from nio.modules.proxy import ProxyNotProxied
from nio.util.threading import spawn


class PublisherNotReadyException(Exception):
    """ Exception raised when publisher is not ready within specified time
    """
    pass


class PublisherProxy(object):

    _publisher = None
    _publisher_lock = RLock()
    # establish that publisher is ready for use
    _publisher_ready_event = Event()
    # many loggers get initialized however, only once the proxy is initialized
    _initialized = False
    # publishing criteria
    _topic = "nio_logging"
    # Maximum time to wait for Publisher to be ready
    _max_publisher_ready_time = 5
    # Interval between sleeps waiting for Publisher to be ready
    _publisher_ready_wait_interval_time = 0.1

    @classmethod
    def init(cls, topic,
             max_publisher_ready_time, publisher_ready_wait_interval_time):
        """ Initializes the proxy

        Args:
            topic (str): topic to use when publishing log messages
            max_publisher_ready_time (float): maximum time to wait for publisher
                to be ready
            publisher_ready_wait_interval_time (float): interval in seconds to
                use when waiting for publisher to be ready
        """
        if not cls._initialized:
            # proxy initialization happens only once
            cls._topic = topic
            cls._max_publisher_ready_time = max_publisher_ready_time
            cls._publisher_ready_wait_interval_time = \
                publisher_ready_wait_interval_time
            spawn(cls._create_publisher)
            cls._initialized = True

    @classmethod
    def publish(cls, signals):
        """ Publishes logging signals.

        This method publishes the signal when publisher has been setup
        successfully.

        It might happen that a call to publish 'logging' signals comes before
        publisher is ready, this is due to the logging module being initialized
        before communication module, in which case the signals are ignored or
        not published

        Note: establishing a mechanism waiting for publisher to be ready during
        this 'publish' call has its own drawbacks due to the fact that the
        original logging instructions might hold back the execution that allows
        a publisher to be ready in the first place (see _create_publisher)

        Args:
            signals: signals to publish

        """
        # publish when all conditions are met
        if cls._publisher_ready_event.is_set():
            with cls._publisher_lock:
                cls._publisher.send(signals)

    @classmethod
    def close(cls):
        """ Closes publisher by releasing all resources """

        if cls._publisher:
            try:
                cls._publisher.close()
            except:
                pass
            finally:
                cls._publisher = None

        cls._publisher_ready_event.clear()
        cls._initialized = False

    @classmethod
    def _create_publisher(cls):
        """ Attempts to create publisher.

        Keeps on trying to create publisher, which will happen successfully
        once communication module is initialized
        """
        end_time = datetime.now() + timedelta(
            seconds=cls._max_publisher_ready_time)
        while not cls._publisher_ready_event.is_set():
            try:
                cls._publisher = Publisher(topic=cls._topic)
                cls._publisher.open()
                cls._publisher_ready_event.set()
            except (ProxyNotProxied, ModuleNotInitialized):
                if datetime.now() >= end_time:
                    raise PublisherNotReadyException(
                        "Maximum time for publisher to be ready elapsed")
                sleep(cls._publisher_ready_wait_interval_time)
