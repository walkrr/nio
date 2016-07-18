""" discoverable and not_discoverable decorators

Classes marked as `discoverable` allow the system to identify them and register
them, while marking a class as  `not_discoverable` produces the opposite effect

n.io will look for services and components marked as `discoverable` and for
blocks marked as `not_discoverable`

Note: A class being marked `discoverable` will not mark its subclasses as
`discoverable`. Each subclass must be explicitly marked with the `discoverable`
decorator, the same applies for `not_discoverable`

To mark a class as not_discoverable, use the parameter-less decorator
`not_discoverable`::

    from nio import not_discoverable, Block

    @not_discoverable
    class MyBlock(Block):
        pass

"""


def discoverable(_class):
    """The decorator method to be called on the class object.

    This method will set the proper discoverable type to the class. It
    should return the class passed in, according to the decorator spec.
    """

    # Set the attribute to the class name, to prevent subclasses from also
    # being discoverable.
    setattr(_class, _get_discoverable_attribute(_class), True)
    return _class


def is_class_discoverable(_class):
    """ Returns true if the class is marked discoverable

    Note: discoverability does not extend to subclasses. Each subclass must
    explicitly be marked as discoverable

    Args:
        _class (class): The class in question, should be a class object

    Returns:
        bool: True if the class is discoverable
    """
    return bool(getattr(_class, _get_discoverable_attribute(_class), False))


def _get_discoverable_attribute(_class):
    """ Get an attribute to set on a class to consider it discoverable """
    return "__{}_is_discoverable".format(_class.__name__)


def not_discoverable(_class):
    """The decorator method to be called on the class object.

    This method will set the proper not discoverable type to the class. It
    should return the class passed in, according to the decorator spec.
    """

    # Set the attribute to the class name, to prevent subclasses from also
    # being not discoverable.
    setattr(_class, _get_not_discoverable_attribute(_class), True)
    return _class


def is_class_not_discoverable(_class):
    """ Returns true if the class is marked not discoverable

    Note: discoverability does not extend to subclasses. Each subclass must
    explicitly be marked as not discoverable

    Args:
        _class (class): The class in question, should be a class object

    Returns:
        bool: True if the class is not discoverable
    """
    return bool(getattr(_class, _get_not_discoverable_attribute(_class), False))


def _get_not_discoverable_attribute(_class):
    """ Get an attribute to set on a class to consider it not discoverable """
    return "__{}_not_discoverable".format(_class.__name__)
