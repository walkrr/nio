
from nio.properties import BaseProperty
from nio.types import Type
from nio.testing.test_case import NIOTestCaseNoModules


class TestOrder(NIOTestCaseNoModules):

    def test_order(self):
        with self.assertRaises(ValueError):
            BaseProperty(Type, title="title", order="str")

        with self.assertRaises(ValueError):
            BaseProperty(Type, title="title", order=2.1)

        property = BaseProperty(Type, title="title", order=12)
        self.assertEqual(property.order, 12)
