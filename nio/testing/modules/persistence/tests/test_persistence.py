from nio.testing.test_case import NIOTestCase
from nio.modules.persistence import Persistence


class TestPersistence(NIOTestCase):

    def get_test_modules(self):
        return super().get_test_modules() | {'persistence'}

    def test_item(self):
        """ Asserts persistence at the item level """

        persist = Persistence()
        persist.save('item_val', 'item_id')

        # Make sure we get the saved value
        self.assertEqual(
            persist.load('item_id', default='not found'),
            'item_val')

        # Make sure we get a default value if one hasn't been saved
        self.assertEqual(
            persist.load('invalid_id', default='default_val'),
            'default_val')

        # Remove item
        persist.remove('item_id')

        # not it behaves as it never existed
        self.assertEqual(
            persist.load('item_id', default='default_val'),
            'default_val')

    def test_collection_item(self):
        """ Asserts item persistence within a collection """

        persist = Persistence()
        persist.save('collection_item_val', 'item_id',
                     collection='item_collection')
        persist.save('item_val', 'item_id')

        # Make sure we get the correct value depending on collection argument
        self.assertEqual(persist.load('item_id', collection='item_collection'),
                         'collection_item_val')
        self.assertEqual(persist.load('item_id'), 'item_val')

        # Remove item
        persist.remove('item_id', collection='item_collection')
        self.assertEqual(persist.load('item_id', collection='item_collection',
                                      default='default_val'),
                         'default_val')

    def test_collection(self):
        """ Asserts collection persistence """

        items = {"item1": "item1_val", "item2": "item2_val"}

        persist = Persistence()
        persist.save_collection(items, 'item_id')

        # load it back and assert results
        self.assertDictEqual(persist.load_collection('item_id'), items)

        # Remove item
        persist.remove_collection('item_id')
        self.assertEqual(persist.load_collection('item_id',
                                                 default='default_val'),
                         'default_val')
