from datetime import timedelta
from unittest.mock import MagicMock, patch
from nio.block.mixins.persistence.persistence import Persistence
from nio.modules.persistence import Persistence as PersistenceModule
from nio.block.base import Block
from nio.testing.block_test_case import NIOBlockTestCase


class PersistingBlock(Persistence, Block):

    def __init__(self):
        super().__init__()
        self._to_be_saved = 'value'
        self._not_to_be_saved = 'value'
        self._to_be_saved_again = 'another value'

    def persisted_values(self):
        """ Overridden to define what is persisted """
        return ["_to_be_saved", "_to_be_saved_again"]


class TestPersistence(NIOBlockTestCase):

    def get_test_modules(self):
        return super().get_test_modules() | {'persistence'}

    def test_saves_properly(self):
        """ Tests that the mixin saves the right values """
        block = PersistingBlock()
        self.configure_block(block, {"name": "test_block"})
        block.start()
        # Stop the block to initiate the save using values specified
        # in block's constructor
        block.stop()

        item = block._persistence.load('test_block')
        # Make sure the right data was saved
        self.assertEqual(len(item), 2)
        self.assertEqual(item['_to_be_saved'], 'value')
        self.assertEqual(item['_to_be_saved_again'], 'another value')

        # remove persisted info.
        PersistenceModule().remove("test_block")

    def test_loads_properly(self):
        """ Tests that the mixin loads into the right values """
        block = PersistingBlock()
        self.configure_block(block, {
            'load_from_persistence': True,
            'name': "test_block"
        })
        block._persistence.save({
            "_to_be_saved": "saved value 1",
            "_to_be_saved_again": "saved value 2"
        }, "test_block")
        # Force the load now - it happened in configure too, but we hadn't
        # overwritten the values yet
        block._load()

        # Make sure the new data was loaded into the right variables
        self.assertEqual(block._to_be_saved, 'saved value 1')
        self.assertEqual(block._to_be_saved_again, 'saved value 2')

        # remove persisted info.
        PersistenceModule().remove("test_block")

    def test_no_load(self):
        """ Tests that the mixin doesn't load if it's told not to """
        block = PersistingBlock()
        block._load = MagicMock()
        self.configure_block(block, {
            'load_from_persistence': False
        })
        # Make sure load wasn't called
        self.assertFalse(block._load.called)
        # We should have the original values too
        self.assertEqual(block._to_be_saved, 'value')
        self.assertEqual(block._to_be_saved_again, 'another value')

    def test_backup_job(self):
        """ Tests that periodic backups occur """
        block = PersistingBlock()
        self.configure_block(block, {
            'backup_interval': {'seconds': 1}
        })
        block._persistence.save = MagicMock()
        with patch('nio.block.mixins.persistence.persistence.Job') as job_mock:
            block.start()
            # Make sure our repeatable job was created properly
            job_mock.assert_called_once_with(
                block._save, timedelta(seconds=1), True)
        # Simulate 2 saves occurring, change the value of the variable once
        block._save()
        block._to_be_saved = 'new_value'
        block._save()
        # Stop the block to initiate one more save
        block.stop()
        # We should have had 3 saves, 2 during execution and 1 on the stop
        self.assertEqual(block._persistence.save.call_count, 3)

    def test_no_backup(self):
        """ Backup interval of 0 means no backing up """
        block = PersistingBlock()
        self.configure_block(block, {
            'backup_interval': {'seconds': 0}
        })
        self.assertIsNone(block._backup_job)
