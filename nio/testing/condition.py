from threading import Event
from time import sleep

from nio.util.threading import spawn


class ConditionWaiter(object):
    def __init__(self, event, callback, *args, sleep_step=0.001, **kwargs):
        self._event = event
        self._callback = callback
        self._sleep_step = sleep_step
        self._args = args
        self._kwargs = kwargs
        self._stopped = False

    def _check_condition(self):
        while not self._stopped:
            sleep(self._sleep_step)
            if self._callback(*self._args, **self._kwargs):
                self._event.set()
                break

    def start(self):
        self._stopped = False
        self._event.clear()
        spawn(self._check_condition)

    def stop(self):
        self._stopped = True


def ensure_condition(callback, *args,
                     sleep_step=0.001, max_wait_time=30, **kwargs):
    """ Waits for a True return from the callback specified

    Args:
        callback: callback to execute, when callback returns True
            the wait is over
        *args: callback arguments
        sleep_step: amount of time to sleep between condition checks
        max_wait_time: maximum amount of time to wait for condition
        **kwargs: callback arguments

    Returns:
        True: if callback at some point return True
        False: if waited maximum time allowed without callback ever
            returning True (CONDITION_EVENT_MAX_WAIT)

    """
    event = Event()
    condition = ConditionWaiter(event, callback, *args,
                                sleep_step=sleep_step, **kwargs)
    condition.start()
    result = event.wait(max_wait_time)
    condition.stop()

    return result
