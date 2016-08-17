from nio.util.threading.thread import NIOThread


def spawn(target, *args, **kwargs):
    """ Executes given target in a new thread

    This method creates a thread invoking the target function specified

    If the target function happens to eventually invoke a longtime running
    function executing in C, the GIL happens to hijack control and would not
    allow the launching thread to continue until the function ends, such
    behaviour can be mitigated by wrapping 'target' in a new function where
    the first instruction is a 'sleep' with a very low number of seconds
    (0.00001 is recommended)

    Args:
        target: method or function to execute
        *args: positional arguments in 'target'
        **kwargs: keyword arguments in 'target'

    Returns:
        newly created thread

    """
    t = NIOThread(target=target, args=args, kwargs=kwargs)
    t.daemon = True
    t.start()
    return t
