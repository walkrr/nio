
from nio.properties import BaseProperty
from nio.types import Type
from nio.testing.test_case import NIOTestCaseNoModules


class TestTitle(NIOTestCaseNoModules):

    def test_title(self):
        with self.assertRaises(ValueError):
            BaseProperty(Type)

        with self.assertRaises(ValueError):
            BaseProperty(Type, title=None)

        with self.assertRaises(ValueError):
            BaseProperty(Type, title="")

        property = BaseProperty(Type, title="non_empty")
        self.assertEqual(property.title, "non_empty")
