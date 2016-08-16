from nio.modules.communication.topic import is_topic_valid
from nio.testing.test_case import NIOTestCase


class TestTopic(NIOTestCase):

    def test_topic(self):
        """ Asserts topic validations
        """

        # assert valid topics
        self.assertTrue(is_topic_valid("A"))
        self.assertTrue(is_topic_valid("A.1"))
        self.assertTrue(is_topic_valid("A.1.a"))
        self.assertTrue(is_topic_valid("A.*"))
        self.assertTrue(is_topic_valid("A.1"))
        self.assertTrue(is_topic_valid("A.1.*"))
        self.assertTrue(is_topic_valid("A.1.a"))
        self.assertTrue(is_topic_valid("A.1.**"))
        self.assertTrue(is_topic_valid("A.**"))
        self.assertTrue(is_topic_valid("A.*.**"))
        self.assertTrue(is_topic_valid("A.*.a"))
        self.assertTrue(is_topic_valid("A.*.a"))
        self.assertTrue(is_topic_valid("A.**.a"))
        self.assertTrue(is_topic_valid("*.a"))
        self.assertTrue(is_topic_valid("**.a"))
        self.assertTrue(is_topic_valid("**.1"))
        self.assertTrue(is_topic_valid("*.1.*"))
        self.assertTrue(is_topic_valid("*.1.**"))
        self.assertTrue(is_topic_valid("*"))
        self.assertTrue(is_topic_valid("*.**"))
        self.assertTrue(is_topic_valid("**"))
        self.assertTrue(is_topic_valid("**.**"))
        self.assertTrue(is_topic_valid("**.*"))
        self.assertTrue(is_topic_valid("*.*.**"))

        # assert invalid topics
        self.assertFalse(is_topic_valid("**."))
        self.assertFalse(is_topic_valid("*."))
        self.assertFalse(is_topic_valid("a."))
        self.assertFalse(is_topic_valid(".a"))
        self.assertFalse(is_topic_valid("a.b."))
        self.assertFalse(is_topic_valid(""))
        self.assertFalse(is_topic_valid("."))
        self.assertFalse(is_topic_valid("m&"))
        self.assertFalse(is_topic_valid("a.m&"))
        self.assertFalse(is_topic_valid("m&.a"))
        self.assertFalse(is_topic_valid("a.m&.a"))
