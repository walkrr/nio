from unittest import skip
from nio.types import BoolType
from nio.types.base import Type
from nio.testing.test_case import NIOTestCase


class TestBool(NIOTestCase):

    def assert_deserialize_equals(self, input_value, output_value):
        nio_type = BoolType
        value_type = bool
        deserialized = nio_type.deserialize(input_value)
        self.assertEqual(deserialized, output_value)
        self.assertEqual(type(deserialized), value_type)

    def test_deserialize_true(self):
        """Deserialize accepts regular True python bool"""
        self.assert_deserialize_equals(True, True)

    def test_deserialize_false(self):
        """Deserialize accepts regular False python bool"""
        self.assert_deserialize_equals(False, False)

    def test_deserialize_true_integers(self):
        """Deserialize accepts non-0 integers as True"""
        for i in range(-10, 0):
            self.assert_deserialize_equals(i, True)
        for i in range(1, 10):
            self.assert_deserialize_equals(i, True)

    def test_deserialize_false_integer(self):
        """Deserialize accepts 0 integers as False"""
        self.assert_deserialize_equals(0, False)

    def test_deserialize_true_strings(self):
        """Deserialize accepts certain strings as True"""
        self.assert_deserialize_equals('True', True)
        self.assert_deserialize_equals('true', True)
        self.assert_deserialize_equals('yes', True)
        self.assert_deserialize_equals('on', True)

    def test_deserialize_false_strings(self):
        """Deserialize accepts certain strings as False"""
        self.assert_deserialize_equals('False', False)
        self.assert_deserialize_equals('false', False)
        self.assert_deserialize_equals('no', False)
        self.assert_deserialize_equals('off', False)
        self.assert_deserialize_equals('', False)

    def test_deserialize_other_true_types(self):
        """Deserialize accepts the natural true-ness of data types"""
        self.assert_deserialize_equals({"value"}, True)
        self.assert_deserialize_equals(["value"], True)

    def test_deserialize_other_false_types(self):
        """Deserialize accepts the natural false-ness of data types"""
        self.assert_deserialize_equals({}, False)
        self.assert_deserialize_equals([], False)
        self.assert_deserialize_equals(None, False)
