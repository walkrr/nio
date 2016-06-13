from threading import RLock, Event
from time import sleep
from datetime import datetime, timedelta

from nio.modules.communication.publisher import Publisher
from nio.util.threading import spawn


class PublisherProxy(object):

    _publisher = None
    _publisher_lock = RLock()
    # establish that publisher is ready for use
    _publisher_ready_event = Event()
    # many loggers get initialized however, only once the proxy is initialized
    _initialized = False
    # publishing criteria
    _topics = {}
    # Maximum time to wait for Publisher to be ready
    MAX_PUBLISHER_READY_TIME = 1
    # Interval between sleeps waiting for Publisher to be ready
    PUBLISHER_READY_WAIT_INTERVAL_TIME = 0.01

    @classmethod
    def init(cls, topics):
        """ Initializes the proxy

        Args:
            topics (dict): topics to use when publishing signals
        """
        if not cls._initialized:
            # proxy initialization happens only once
            cls._topics = topics
            spawn(cls._create_publisher)
            cls._initialized = True

    @classmethod
    def publish(cls, signals):
        """ Publishes logging signals.

        This method ensures that publisher is ready to send signals, it
        might happen that a call to publish 'logging' signals might come before
        publisher is ready since logging is initialized before communication


        Args:
            signals: signals to publish

        """
        # publish when all conditions are met
        cls._ensure_publisher_ready()
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
    def _ensure_publisher_ready(cls):
        """ Ensures publisher is ready before any publishing takes place
        """
        if not cls._publisher_ready_event.is_set():
            cls._publisher_ready_event.wait(cls.MAX_PUBLISHER_READY_TIME)

    @classmethod
    def _create_publisher(cls):
        """ Keeps on trying to create publisher, which will happen
        successfully once communication module is initialized
        """
        end_time = datetime.now() + timedelta(
            seconds=cls.MAX_PUBLISHER_READY_TIME)
        while not cls._publisher_ready_event.is_set():
            try:
                cls._publisher = Publisher(**cls._topics)
                cls._publisher.open()
                cls._publisher_ready_event.set()
            except NotImplementedError:
                if datetime.now() >= end_time:
                    raise RuntimeError("Maximum time for publisher "
                                       "to be ready elapsed")
                sleep(cls.PUBLISHER_READY_WAIT_INTERVAL_TIME)
