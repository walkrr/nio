import functools
import re


def add_regex_ending(regex):
    """ Utility function to add a regular expression ending

    Args:
        regex (str): Incoming regular expression

    Returns:
        Same regular expression plus ending
    """
    return regex + "\Z"


def translate_to_regex(pat):
    """ Translate a topic pattern to regular expression

    The algorithm analizes the pattern once character at a time and handles
    '*' and '.' as special characters that in combination can have a special
    meaning such as (*., .*, **., .**, etc)

    Most likely this function will return a single regular expression, however,
    depending on the pattern, more than one expression might be returned in
    order to accommodate exceptions to the pattern that could be seen as
    acceptable matches.

    Args:
        pat (str): pattern to translate

    Returns:
        list of regular expressions
    """
    i = 0
    n = len(pat)
    res = ''
    while i < n:
        if pat[i] == '*':
            # is it a '**' between dots?
            if pat[i-1: i+3] == ".**.":
                res += '.*'
                i += 1
            # is it a '*' between dots?
            elif pat[i-1: i+2] == ".*.":
                res += '.[^.]*'
            # is it a '**' at the beginning following by a dot?
            elif i == 0 and pat[i: i + 3] == "**.":
                res += '.*'
                i += 1
            # is it a '*' at the beginning following by a dot?
            elif i == 0 and pat[i: i + 2] == "*.":
                res += '.[^.]*'
            # is it a '.**' at the end?
            elif i+2 == n and pat[i-1: i+2] == ".**":
                # return two expressions to accommodate (pattern=pattern.**),
                # second expression removes "." from regex
                return [add_regex_ending(res + ".*"),
                        add_regex_ending(res[:len(res)-len(re.escape('.'))])]
            # is it a '.*' at the end?
            elif i+1 == n and pat[i-1: i+1] == ".*":
                # return two expressions to accommodate (pattern=pattern.*),
                # second expression removes "." from regex
                return [add_regex_ending(res + ".*"),
                        add_regex_ending(res[:len(res)-len(re.escape('.'))])]
            else:
                # consider it a regular character
                res = res + re.escape(pat[i])
        else:
            res = res + re.escape(pat[i])
        i += 1
    return [add_regex_ending(res)]


@functools.lru_cache()
def _compile_pattern(pat):
    """ Compiles a pattern returning match operations to evaluate against.

    Args:
        pat (str): Pattern string

    Returns:
        list of match objects

    """
    expressions = translate_to_regex(pat)
    return [re.compile(expression).match for expression in expressions]


def matches(sub_topic, pub_topic):
    """ Finds out if there is a match between publisher and subscriber

    Args:

        sub_topic (str): Subscriber topic (can contain wildcards)
        pub_topic (str): Publisher topic

    Return:
        True if they match, False otherwise
    """
    pub_topic = pub_topic.strip()
    sub_topic = sub_topic.strip()
    if pub_topic == sub_topic or sub_topic == "*":
        # trivial cases where pub and sub topic are the same or
        # sub_topic specifies a subscription to everything.
        return True

    if pub_topic.startswith(sub_topic):
        # sub_topic is a prefix
        if sub_topic.endswith(".") or pub_topic.startswith(sub_topic + "."):
            # in order to match, sub_topic ends with "." or
            # sub_topic is a prefix where adding "." to it is also a prefix
            return True

    # if a pattern is specified, handle it using regular expressions
    if '*' in sub_topic:
        compiled_matches = _compile_pattern(sub_topic)
        for compiled_match in compiled_matches:
            if compiled_match(pub_topic) is not None:
                return True

    return False
