
from nio.testing.block import NIOBlockTestCase


class TestBlockType(NIOBlockTestCase):

    def test_block_type(self):
        """ Asserts that block type must be specified

        To specify the block type for tests within class test type
        override the block_type get property, i.e.,

            @property
            def block_type(self):
                return MyBlockType

        """
        with self.assertRaises(TypeError):
            self.configure_block({})

        # any attempt to access 'block' member before setting block_type
        # raises an exception
        with self.assertRaises(TypeError):
            self.assertIsNone(self.block)
