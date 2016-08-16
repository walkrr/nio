import re

# defines allowed characters withing a topic level
LEVEL_ALLOWED_CHARACTERS = "[0-9A-Za-z_\* \-]"
# pre-compiled match for allowed characters withing a level
level_match = re.compile("^{}+$".format(LEVEL_ALLOWED_CHARACTERS))


class InvalidTopic(Exception):
    """ Exception to be raised when a topic is invalid
    """
    pass


def is_topic_valid(topic):
    """ Finds out if a given topic is valid

    Topic should be validated when instantiating a Publisher or a Subscriber
    matching algorithm assumes topics are valid.

    Args:
        topic: topic to validate

    Returns:
        True if topic is valid, False otherwise
    """
    sub_topics = topic.split('.')
    for sub_topic in sub_topics:
        # validate topic level
        if not level_match.match(sub_topic):
            return False

    return True
