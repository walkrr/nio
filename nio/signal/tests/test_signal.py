import copy
import datetime
from nio.signal.base import Signal
from nio.testing.test_case import NIOTestCase


class TestSignal(NIOTestCase):

    def setUp(self):
        super().setUp()
        self.attrs = {
            'foo': 'bar',
            'num': 3,
            'dt': datetime.date(2010, 3, 14)
        }

    def test_from_dict(self):
        """ Ensure we can merge a dictionary into a signal """
        sig = Signal()
        self.assertFalse(hasattr(sig, 'foo'))
        sig.from_dict(self.attrs)
        self.assertTrue(hasattr(sig, 'foo'))
        self.assertEqual(sig.foo, 'bar')

    def test_invalid_from_dict(self):
        """ Ensure from_dict must receive a dictionary """
        with self.assertRaises(TypeError):
            Signal(attrs="string")

        s = Signal()
        with self.assertRaises(TypeError):
            s.from_dict(333)

    def test_construct(self):
        """ Ensure we can pass a dictionary to the signal constructor """
        sig = Signal(self.attrs)
        self.assertTrue(hasattr(sig, 'foo'))
        self.assertEqual(sig.foo, 'bar')

    def test_signal_str(self):
        """ Assert that str-ing a signal calls to_dict on it"""
        sig = Signal(self.attrs)
        sig_str = str(sig)
        # Can only compare lengths since str changes the order some time
        self.assertEqual(len(sig_str), len(str(self.attrs)))

    def test_no_hidden(self):
        """ Ensure that hidden attributes are not returned by default """
        sig = Signal({
            'not_hidden': 'yes',
            '_hidden': 'no',
            '__double_hidden': 'no'
        })
        self.assertIn('not_hidden', sig.to_dict())
        self.assertNotIn('_hidden', sig.to_dict())
        self.assertNotIn('__double_hidden', sig.to_dict())

    def test_to_dict_with_type(self):
        """ Ensure we can get the teyp of a signal """
        sig = Signal(self.attrs)
        signal_dict = sig.to_dict(with_type="_type")
        self.assertIn('_type', signal_dict)
        self.assertEqual(signal_dict['_type'], 'Signal')
        self.assertIn('foo', signal_dict)

    def test_to_dict_keeps_types(self):
        """ Ensure that to_dict keeps the original types of data """
        sig = Signal(self.attrs)
        signal_dict = sig.to_dict()
        self.assertEqual(signal_dict['num'], 3)
        self.assertEqual(signal_dict['dt'], datetime.date(2010, 3, 14))

    def test_to_dict_with_errors(self):
        """ Ensure that invalid object attributes are not set on the signal """
        with self.assertRaises(ValueError):
            Signal({'': 'empty string'})
        with self.assertRaises(ValueError):
            Signal({None: 'none key'})
        with self.assertRaises(ValueError):
            Signal({False: 'false key'})
        with self.assertRaises(ValueError):
            Signal({1: "one"})

        sig = Signal({"allowed": "allowed_value"})
        self.assertTrue(hasattr(sig, "allowed"))

    def test_to_dict_with_hidden(self):
        """ Ensure that hidden attributes can be accessed via to_dict """
        attributes = copy.deepcopy(self.attrs)
        attributes["_hidden1"] = "hidden1"
        attributes["_hidden2"] = "hidden2"
        attributes["__double_hidden"] = "double_hidden"
        sig = Signal(attributes)
        signal_dict = sig.to_dict(include_hidden=True)
        for key, value in self.attrs.items():
            self.assertEqual(signal_dict[key], value)
        self.assertEqual(signal_dict['_hidden1'], attributes["_hidden1"])
        self.assertEqual(signal_dict['_hidden2'], attributes["_hidden2"])
        self.assertNotIn('__double_hidden', signal_dict)

        # use default
        signal_dict = sig.to_dict()
        for key, value in self.attrs.items():
            self.assertEqual(signal_dict[key], value)
        self.assertNotIn('_hidden1', signal_dict)
        self.assertNotIn('_hidden2', signal_dict)
        self.assertNotIn('__double_hidden', signal_dict)

    def test_signal_equality_comparison(self):
        """ Ensure that two signals can compare equality """
        sig1 = Signal(self.attrs)
        sig2 = Signal(self.attrs)
        self.assertTrue(sig1 == sig2)
        self.assertTrue(sig2 == sig1)
        # object identity should be different even with equal value
        self.assertIsNot(sig1, sig2)

        # if lists differ in order they are not equal
        sig1 = Signal({"hello": [1, 2, 3]})
        sig2 = Signal({"hello": [3, 2, 1]})
        self.assertFalse(sig1 == sig2)
        self.assertFalse(sig2 == sig1)
