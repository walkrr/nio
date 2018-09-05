from datetime import timedelta
from unittest.mock import MagicMock, patch

from nio.block.base import Block
from nio.block.mixins.persistence.persistence import Persistence
from nio.modules.persistence import Persistence as PersistenceModule
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
        self.configure_block(block, {"id": "test_block"})
        block.start()
        # Stop the block to initiate the save using values specified
        # in block's constructor
        block.stop()

        item = block._persistence.load(block.id())
        # Make sure the right data was saved
        self.assertEqual(len(item), 2)
        self.assertEqual(item['_to_be_saved'], 'value')
        self.assertEqual(item['_to_be_saved_again'], 'another value')

    def test_loads_properly(self):
        """ Tests that the mixin loads into the right values """
        block = PersistingBlock()
        self.configure_block(block, {
            'load_from_persistence': True,
            'id': 'test_block'
        })
        block._persistence.save({
            "_to_be_saved": "saved value 1",
            "_to_be_saved_again": "saved value 2"
        }, block.id())
        # Force the load now - it happened in configure too, but we hadn't
        # overwritten the values yet
        block._load()

        # Make sure the new data was loaded into the right variables
        self.assertEqual(block._to_be_saved, 'saved value 1')
        self.assertEqual(block._to_be_saved_again, 'saved value 2')

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

    def test_block_loading_from_persistence(self):
        """ Tests saving to persistence outside of block

        Makes sure data that even though data was saved outside of block, it
        can be picked up by block's persistence
        """

        block_id = 'test_block'
        # save data under block id
        PersistenceModule().save(
            {'_to_be_saved': 3,
             '_to_be_saved_again': 4},
            block_id)

        block = PersistingBlock()
        # make block load from persistence
        self.configure_block(block,
                             {'id': 'test_block',
                              'load_from_persistence': True
                              })
        # assert that data matches what was persisted outside of block
        self.assertEqual(block._to_be_saved, 3)
        self.assertEqual(block._to_be_saved_again, 4)


class SerializingBlock(Persistence, Block):

    def __init__(self):
        super().__init__()
        self._attr1 = "attr1 default"
        self._attr2 = "attr2 default"
        # attr3 is ignored in serialize/deserialize yet considered in
        # persisted_values, used to show that it is ignored, since
        # serialize/deserialize takes precedence
        self._attr3 = "attr3 default"
        self._not_to_be_saved = 'not_to_be_saved'

    def serialize(self):
        """ Overridden to define what is persisted """
        return {
            "attr1": self._attr1,
            "attr2": self._attr2
        }

    def deserialize(self, data):
        """ Overridden to define what is loaded """
        self._attr1 = data["attr1"]
        self._attr2 = data["attr2"]

    def persisted_values(self):
        """ Defined just to show precedence

        It will not be saved
        """
        return ["_attr3"]


class TestSerialize(NIOBlockTestCase):

    def test_configures_from_scratch(self):
        """ Tests that block configures even when there is nothing to load

        Shows that when block is first instantiated and configured with no data
        previously persisted no errors occur
        """
        block = SerializingBlock()
        block_id = "test_block1"

        self.configure_block(block, {"id": block_id})
        self.assertEqual(block._not_to_be_saved, "not_to_be_saved")

    def test_load_and_saves_properly(self):
        """ Tests that the mixin saves the right values
        """
        block = SerializingBlock()

        block_id = "test_block2"
        PersistenceModule().save(
            {
                'attr1': 3,
                'attr2': 4,
                # attr3 is saved but ignored in serialize/deserialize
                'attr3': 5
            },
            block_id)

        self.configure_block(block, {"id": block_id})
        self.assertEqual(block._attr1, 3)
        self.assertEqual(block._attr2, 4)
        # was not overriden, even though it was saved, but deserialize
        # ignores it
        self.assertEqual(block._attr3, "attr3 default")
        self.assertEqual(block._not_to_be_saved, "not_to_be_saved")

        block.start()

        # override attr1
        block._attr1 = "new value"
        # override not serializable attrs
        block._attr3 = "new attr3 value"
        block._not_to_be_saved = "new not_to_be_saved"

        # Stop the block to initiate the save using values specified
        # in block's constructor
        block.stop()

        item = block._persistence.load(block.id())
        # Make sure the right data was saved,
        # 2 items means `attr3` nor `not_to_be_saved` were saved/loaded
        self.assertEqual(len(item), 2)
        self.assertEqual(item['attr1'], "new value")
        self.assertEqual(item['attr2'], 4)
