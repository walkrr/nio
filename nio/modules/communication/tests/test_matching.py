from nio.modules.communication.matching import matches
from nio.testing.test_case import NIOTestCase


class TestMatching(NIOTestCase):

    def test_matching(self):
        """ Asserts matching algorithm
        """

        # prefix are a match up to a dot
        self.assertTrue(matches("a", "a"))
        self.assertTrue(matches("a", "a.b1"))
        self.assertTrue(matches("a", "a.b1.c1"))
        self.assertTrue(matches("a", "a.b1.c1.end"))
        self.assertTrue(matches("a", "a.b1.end"))
        self.assertTrue(matches("a", "a.b2"))
        self.assertTrue(matches("a", "a.b2.end"))
        # it is a prefix but after adding a dot (simulate level) to it,
        # it ceases to be a prefix
        self.assertFalse(matches("a", "a2"))
        self.assertFalse(matches("a", "a2.end"))

        self.assertFalse(matches("a.b1", "a"))
        self.assertTrue(matches("a.b1", "a.b1"))
        self.assertTrue(matches("a.b1", "a.b1.c1"))
        self.assertTrue(matches("a.b1", "a.b1.c1.end"))
        self.assertTrue(matches("a.b1", "a.b1.end"))
        self.assertFalse(matches("a.b1", "a.b2"))
        self.assertFalse(matches("a.b1", "a.b2.end"))
        self.assertFalse(matches("a.b1", "a2"))
        self.assertFalse(matches("a.b1", "a2.end"))

        self.assertFalse(matches("a.b1.c1", "a"))
        self.assertFalse(matches("a.b1.c1", "a.b1"))
        self.assertTrue(matches("a.b1.c1", "a.b1.c1"))
        self.assertTrue(matches("a.b1.c1", "a.b1.c1.end"))
        self.assertFalse(matches("a.b1.c1", "a.b1.end"))
        self.assertFalse(matches("a.b1.c1", "a.b2"))
        self.assertFalse(matches("a.b1.c1", "a.b2.end"))
        self.assertFalse(matches("a.b1.c1", "a2"))
        self.assertFalse(matches("a.b1.c1", "a2.end"))

        self.assertFalse(matches("a.b1.c1.end", "a"))
        self.assertFalse(matches("a.b1.c1.end", "a.b1"))
        self.assertFalse(matches("a.b1.c1.end", "a.b1.c1"))
        self.assertTrue(matches("a.b1.c1.end", "a.b1.c1.end"))
        self.assertFalse(matches("a.b1.c1.end", "a.b1.end"))
        self.assertFalse(matches("a.b1.c1.end", "a.b2"))
        self.assertFalse(matches("a.b1.c1.end", "a.b2.end"))
        self.assertFalse(matches("a.b1.c1.end", "a2"))
        self.assertFalse(matches("a.b1.c1.end", "a2.end"))

        self.assertFalse(matches("a.b2", "a"))
        self.assertFalse(matches("a.b2", "a.b1"))
        self.assertFalse(matches("a.b2", "a.b1.c1"))
        self.assertFalse(matches("a.b2", "a.b1.c1.end"))
        self.assertFalse(matches("a.b2", "a.b1.end"))
        self.assertTrue(matches("a.b2", "a.b2"))
        self.assertTrue(matches("a.b2", "a.b2.end"))
        self.assertFalse(matches("a.b2", "a2"))
        self.assertFalse(matches("a.b2", "a2.end"))

        self.assertFalse(matches("a.end", "a"))
        self.assertFalse(matches("a.end", "a.b1"))
        self.assertFalse(matches("a.end", "a.b1.c1"))
        self.assertFalse(matches("a.end", "a.b1.c1.end"))
        self.assertFalse(matches("a.end", "a.b1.end"))
        self.assertFalse(matches("a.end", "a.b2"))
        self.assertFalse(matches("a.end", "a.b2.end"))
        self.assertFalse(matches("a.end", "a2"))
        self.assertFalse(matches("a.end", "a2.end"))

        # will match topics with just one level before '.end'
        self.assertFalse(matches("*.end", "a"))
        self.assertFalse(matches("*.end", "a.b1"))
        self.assertFalse(matches("*.end", "a.b1.c1"))
        # right ending but more than one level deep
        self.assertFalse(matches("*.end", "a.b1.c1.end"))
        self.assertFalse(matches("*.end", "a.b1.end"))
        self.assertFalse(matches("*.end", "a.b2"))
        self.assertFalse(matches("*.end", "a.b2.end"))
        self.assertFalse(matches("*.end", "a2"))
        self.assertTrue(matches("*.end", "a2.end"))

        # will match topics with multiple levels ending in '.end'
        self.assertFalse(matches("**.end", "a"))
        self.assertFalse(matches("**.end", "a.b1"))
        self.assertFalse(matches("**.end", "a.b1.c1"))
        self.assertTrue(matches("**.end", "a.b1.c1.end"))
        self.assertTrue(matches("**.end", "a.b1.end"))
        self.assertFalse(matches("**.end", "a.b2"))
        self.assertTrue(matches("**.end", "a.b2.end"))
        self.assertFalse(matches("**.end", "a2"))
        self.assertTrue(matches("**.end", "a2.end"))

        # will match topics with only one level between 'a.' and '.end'
        self.assertFalse(matches("a.*.end", "a"))
        self.assertFalse(matches("a.*.end", "a.b1"))
        self.assertFalse(matches("a.*.end", "a.b1.c1"))
        self.assertFalse(matches("a.*.end", "a.b1.c1.end"))
        self.assertTrue(matches("a.*.end", "a.b1.end"))
        self.assertFalse(matches("a.*.end", "a.b2"))
        self.assertTrue(matches("a.*.end", "a.b2.end"))
        self.assertFalse(matches("a.*.end", "a2"))
        self.assertFalse(matches("a.*.end", "a2.end"))

        # will match topics with multiple levels between 'a.' and '.end'
        self.assertFalse(matches("a.**.end", "a"))
        self.assertFalse(matches("a.**.end", "a.b1"))
        self.assertFalse(matches("a.**.end", "a.b1.c1"))
        self.assertTrue(matches("a.**.end", "a.b1.c1.end"))
        self.assertTrue(matches("a.**.end", "a.b1.end"))
        self.assertFalse(matches("a.**.end", "a.b2"))
        self.assertTrue(matches("a.**.end", "a.b2.end"))
        self.assertFalse(matches("a.**.end", "a2"))
        self.assertFalse(matches("a.**.end", "a2.end"))

        # will match topics with two levels between 'a.' and '.end'
        self.assertFalse(matches("a.*.*.end", "a"))
        self.assertFalse(matches("a.*.*.end", "a.b1"))
        self.assertFalse(matches("a.*.*.end", "a.b1.c1"))
        self.assertTrue(matches("a.*.*.end", "a.b1.c1.end"))
        self.assertFalse(matches("a.*.*.end", "a.b1.end"))
        self.assertFalse(matches("a.*.*.end", "a.b2"))
        self.assertFalse(matches("a.*.*.end", "a.b2.end"))
        self.assertFalse(matches("a.*.*.end", "a2"))
        self.assertFalse(matches("a.*.*.end", "a2.end"))

        # more prefix mismatches
        self.assertFalse(matches("ab", "a"))
        self.assertFalse(matches("ab", "a.b1"))
        self.assertFalse(matches("ab", "a.b1.c1"))
        self.assertFalse(matches("ab", "a.b1.c1.end"))
        self.assertFalse(matches("ab", "a.b1.end"))
        self.assertFalse(matches("ab", "a.b2"))
        self.assertFalse(matches("ab", "a.b2.end"))
        self.assertFalse(matches("ab", "a2"))
        self.assertFalse(matches("ab", "a2.end"))

        # empty string does not match anything
        self.assertFalse(matches("", "a"))
        self.assertFalse(matches("", "a.b1"))
        self.assertFalse(matches("", "a.b1.c1"))
        self.assertFalse(matches("", "a.b1.c1.end"))
        self.assertFalse(matches("", "a.b1.end"))
        self.assertFalse(matches("", "a.b2"))
        self.assertFalse(matches("", "a.b2.end"))
        self.assertFalse(matches("", "a2"))
        self.assertFalse(matches("", "a2.end"))

        # when '*' is not along a dot, it is just like any other character
        self.assertFalse(matches("a*", "a"))
        self.assertFalse(matches("a*", "a.b1"))
        self.assertFalse(matches("a*", "a.b1.c1"))
        self.assertFalse(matches("a*", "a.b1.c1.end"))
        self.assertFalse(matches("a*", "a.b1.end"))
        self.assertFalse(matches("a*", "a.b2"))
        self.assertFalse(matches("a*", "a.b2.end"))
        self.assertFalse(matches("a*", "a2"))
        self.assertFalse(matches("a*", "a2.end"))

        # .* at the end is the same as .** (can match many levels)
        self.assertTrue(matches("a.*", "a"))
        self.assertTrue(matches("a.*", "a.b1"))
        self.assertTrue(matches("a.*", "a.b1.c1"))
        self.assertTrue(matches("a.*", "a.b1.c1.end"))
        self.assertTrue(matches("a.*", "a.b1.end"))
        self.assertTrue(matches("a.*", "a.b2"))
        self.assertTrue(matches("a.*", "a.b2.end"))
        self.assertFalse(matches("a.*", "a2"))
        self.assertFalse(matches("a.*", "a2.end"))

        self.assertTrue(matches("a.**", "a"))
        self.assertTrue(matches("a.**", "a.b1"))
        self.assertTrue(matches("a.**", "a.b1.c1"))
        self.assertTrue(matches("a.**", "a.b1.c1.end"))
        self.assertTrue(matches("a.**", "a.b1.end"))
        self.assertTrue(matches("a.**", "a.b2"))
        self.assertTrue(matches("a.**", "a.b2.end"))
        self.assertFalse(matches("a.**", "a2"))
        self.assertFalse(matches("a.**", "a2.end"))

        # a single '*' matches everything
        self.assertTrue(matches("*", "a"))
        self.assertTrue(matches("*", "a.b1"))
        self.assertTrue(matches("*", "a.b1.c1"))
        self.assertTrue(matches("*", "a.b1.c1.end"))
        self.assertTrue(matches("*", "a.b1.end"))
        self.assertTrue(matches("*", "a.b2"))
        self.assertTrue(matches("*", "a.b2.end"))
        self.assertTrue(matches("*", "a2"))
        self.assertTrue(matches("*", "a2.end"))

        # additional prefix tests
        self.assertTrue(matches("a.b.", "a.b.c"))
        self.assertTrue(matches("a", "a."))
        # a level specified that is not in published topic makes it not a match
        self.assertFalse(matches('a.b.', 'a.b'))

        # asserting several level wildcards
        self.assertTrue(matches("*.*.c.*", "a.b.c.d"))
        self.assertTrue(matches("*.*.c.d.*", "a.b.c.d"))
        self.assertTrue(matches("*.*.c.d.*", "a.b.c.d.e"))

        self.assertFalse(matches('a.**.*', 'a'))
        # matches because a.* == a, so it matches
        # if a.** matches a.b, which is the case
        self.assertTrue(matches('a.**.*', 'a.b'))
        # clearly a match
        self.assertTrue(matches('a.**.*', 'a.b.c'))
        # not a match, no need to specify extra .**,
        # kind of an extra unneeded level
        self.assertFalse(matches('a.**.**', 'a'))
        # matches because a.** == a, so it matches
        # if a.** matches a.b, which is the case
        self.assertTrue(matches('a.**.**', 'a.b'))
        # a clear match, levels match nicely
        self.assertTrue(matches('a.**.**', 'a.b.c'))

        self.assertFalse(matches("root.node1", "root.node2"))
        self.assertFalse(matches("root1.node1", "root.node1"))
        self.assertTrue(matches("*.*", "root.node1"))

        # spaces are trimmed at each end of the topic
        self.assertTrue(matches('  a', 'a   '))
        self.assertTrue(matches('  a', 'a'))
        self.assertTrue(matches('a  ', 'a'))
        self.assertTrue(matches('   a   ', 'a'))
        # not a match, spaces inside topic are just another character
        self.assertFalse(matches('a.  b  ', 'a.b'))

