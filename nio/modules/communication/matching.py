import functools
import re

from nio.modules.communication.topic import LEVEL_ALLOWED_CHARACTERS, \
    is_topic_type_valid


# defines level separator
LEVEL_SEPARATOR = re.escape(".")


def _add_regex_ending(regex):
    """ Utility function to add a regular expression ending

    Args:
        regex (str): Incoming regular expression

    Returns:
        Same regular expression plus ending
    """
    return regex + "\Z"


def _translate_to_regex(pattern):
    """ Translate a topic pattern to regular expression

    Algorithm:
        Split subscriber string around “.”
        for each substring (each substring defines a level)
            Replace any double “**” with zero or more allowable
                set of characters
            Replace any “*” single with a single allowable
                set of characters
            Escape any “*” characters when using it along with other characters
        Join together all subscriber topic string regexes

    Args:
        pattern (str): pattern to translate

    Returns:
        A regular expression that will match all valid publishers.
        Note that in order to simplify the level matching, this regex expects
        every level of the topic tree to end with a level separator (.).
        This includes the lowest level of the tree. In other words, make sure
        your publisher topic strings also end with a . before matching them to
        this regular expression.
    """
    sub_patterns = pattern.split('.')
    for i in range(len(sub_patterns)):
        if sub_patterns[i] == "**":
            # allow 0 or more levels
            sub_patterns[i] = \
                "({}+{})*".format(LEVEL_ALLOWED_CHARACTERS, LEVEL_SEPARATOR)
        elif sub_patterns[i] == "*":
            # allow 1 level
            sub_patterns[i] = \
                "{}+{}".format(LEVEL_ALLOWED_CHARACTERS, LEVEL_SEPARATOR)
        elif "*" in sub_patterns[i]:
            sub_patterns[i] = \
                "{}{}".format(sub_patterns[i].replace('*', re.escape('*')),
                              LEVEL_SEPARATOR)
        else:
            sub_patterns[i] = "{}{}".format(sub_patterns[i], LEVEL_SEPARATOR)

    return _add_regex_ending(''.join(sub_patterns))


@functools.lru_cache()
def _compile_pattern(pattern):
    """ Compiles a pattern returning match operations to evaluate against.

    Args:
        pattern (str): Pattern string

    Returns:
        list of match objects

    """
    expression = _translate_to_regex(pattern)
    return re.compile(expression).match


def matches(sub_topic, pub_topic):
    """ Finds out if there is a match between publisher and subscriber

    Assumes that both topics have been validated using 'is_topic_valid'
    Note: Validation is expected to take place within module's implementation.

    Args:
        sub_topic (str): Subscriber topic (can contain wildcards)
        pub_topic (str): Publisher topic

    Return:
        True if they match, False otherwise
    """
    if not is_topic_type_valid(pub_topic) or \
       not is_topic_type_valid(sub_topic):
        # no possible match with an invalid topic
        return False

    # Add a trailing dot to the publisher topic to match the entire level
    # in the regex
    pub_topic += "."

    # compile sub_topic pattern as a regex and match it
    compiled_match = _compile_pattern(sub_topic)
    if compiled_match(pub_topic) is not None:
        return True

    return False
