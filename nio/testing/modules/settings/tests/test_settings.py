from nio.testing.modules.settings import Settings
from nio.testing.test_case import NIOTestCase


class TestSettings(NIOTestCase):

    def test_clear(self):
        settings = {'attr1': 'value1', 'attr2': 'value2'}
        Settings.set('attrs', value=settings)

        self.assertEqual(2, len(Settings.get()["attrs"]))
        Settings.clear()
        self.assertEqual(0, len(Settings.get()))

    def test_get(self):
        settings = {'float_attr': '1.2',
                    'int_attr': '1',
                    'boolean_attr': 'True'}
        Settings.set('attrs', value=settings)

        value = Settings.get("attrs", fallback={})
        self.assertDictEqual(value, settings)

        # assert that sub_entry is returned without conversion
        value = Settings.get("attrs", 'float_attr', fallback=0.5)
        self.assertEqual(value, '1.2')
        self.assertEqual(Settings.get('attrs', 'int_attr'), '1')
        self.assertEqual(Settings.get('attrs', 'boolean_attr'), 'True')
        # assert that converted sub_entry is returned
        value = Settings.getfloat("attrs", 'float_attr', fallback=0.5)
        self.assertEqual(value, 1.2)
        self.assertEqual(Settings.getint('attrs', 'int_attr'), 1)
        self.assertEqual(Settings.getboolean('attrs', 'boolean_attr'), True)

        # assert that default is returned if not a valid sub_entry
        value = Settings.getfloat("attrs", 'not_an_attr', fallback=0.5)
        self.assertEqual(value, 0.5)
        # assert that default is returned if not a valid sub_entry
        value = Settings.get("attrs", 'not_an_attr', fallback=0.5)
        self.assertEqual(value, 0.5)
        value = Settings.get("not_an_entry", fallback=0.5)
        self.assertEqual(value, 0.5)

        # assert that settings returns None if the entry is not
        # found and no default is given
        value = Settings.get("bogon")
        self.assertIsNone(value)

    def test_set(self):

        # Assert that a whole section can be set in one shot
        Settings.set('test_section', value={"int_attr": '1',
                                            'float_attr': 1.2})
        self.assertEqual(Settings.getint('test_section', 'int_attr'), 1)
        self.assertEqual(Settings.getfloat('test_section', 'float_attr'), 1.2)

        # Assert that options can be set individually
        Settings.set('test_section', "boolean_attr", 'True')
        self.assertTrue(Settings.getboolean('test_section', 'boolean_attr'))

        # Assert that previous values remain
        self.assertEqual(Settings.getint('test_section', 'int_attr'), 1)
        self.assertEqual(Settings.getfloat('test_section', 'float_attr'), 1.2)

        # Assert that an option can be set to a brand new section
        Settings.set('new_section', "boolean_attr", 'True')
        self.assertTrue(Settings.getboolean('new_section', 'boolean_attr'))

