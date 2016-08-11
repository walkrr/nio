
from nio.block.base import Block
from nio.testing.block import NIOBlockTestCase


class TestBlockType(NIOBlockTestCase):

    def test_block_type(self):
        """ Asserts that block type must be specified

        There are different ways to specify the block type
            - override block_type get property (useful when all tests in the
                file use the same block_type)

                @property
                def block_type(self):
                    return MyBlockType

            - override setUp method (useful when all tests in the
                file use the same block_type)

                def setUp(self):
                    super().setUp()
                    self.block_type = MyBlockType

            - specify in every test (useful when tests  will use different
                block type classes)

                def test_my_block_type(self):
                    self.block_type = MyBlockType
                    self.configure_block({})
                    ...

        """
        with self.assertRaises(TypeError):
            self.configure_block({})

        # any attempt to access 'block' member before setting block_type
        # raises an exception
        with self.assertRaises(TypeError):
            self.assertIsNone(self.block)

        self.block_type = Block
        self.assertIsNotNone(self.block)

        self.configure_block({})
        self.start_block()
        self.stop_block()
