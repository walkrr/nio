from os import path, remove

from nio.testing.test_case import NIOTestCase
from nio.util.codec import load_json, load_pickle, save_json, save_pickle


class TestCodec(NIOTestCase):

    def setUp(self):
        self.test_dict = {'foobar': 2, 'bazqux': 4}

    def tearDown(self):
        for fname in ['tmp.json', 'tmp.pickle']:
            if path.isfile(fname):
                remove(fname)

    def test_json(self):
        """ Asserts saving and loading json data
        """
        save_json('tmp.json', self.test_dict)
        data = load_json('tmp.json')
        self.assertDictEqual(data, self.test_dict)

    def test_pickle(self):
        """ Asserts saving and loading pickle data
        """
        save_pickle('tmp.pickle', self.test_dict)
        data = load_pickle('tmp.pickle')
        self.assertDictEqual(data, self.test_dict)
