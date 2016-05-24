from unittest.mock import patch
from nio.util.versioning.check import get_major_version
from nio.util.versioning.dependency import validate_version
from nio.util.versioning.tests import module_version, \
    block_b_module_version, block_a_module_version
from nio.testing.test_case import NIOTestCase


class TestVersioning(NIOTestCase):
    @patch('nio.util.versioning.dependency.validate_version')
    def test_version_ok(self, mock_validate):
        mock_validate.return_value = True
        from nio.util.versioning.tests.block_a import BlockA

        mock_validate.assert_called_once_with(module_version,
                                              block_a_module_version)

    @patch('nio.util.versioning.dependency.validate_version')
    def test_version_not_ok(self, mock_validate):
        mock_validate.return_value = False
        from nio.util.versioning.tests.block_b import BlockB
        mock_validate.assert_called_once_with(module_version,
                                              block_b_module_version)

    def test_none_version_comparisons(self):
        self.assertTrue(validate_version("1.1.1", None))
        self.assertTrue(validate_version(None, "1.1.1"))
        self.assertTrue(validate_version(None, None))

    def test_version_comparisons(self):

        # assert that alpha, beta and release candidates versions are allowed
        self.assertTrue(validate_version("1.0.0b6", "1.0.0b5"))
        self.assertTrue(validate_version("1.0.0rc2", "1.0.0rc1"))
        self.assertTrue(validate_version("1.0.0rc1", "1.0.0b1"))
        self.assertTrue(validate_version("1.0.0b1", "1.0.0a1"))
        self.assertTrue(validate_version("1.0.0a2", "1.0.0a1"))

        # assert that an item with version 0.1.0 is not valid when
        # 1.0.0 is called for
        self.assertFalse(validate_version("0.1.0", "1.0.0"))

        # versions matching are ok
        self.assertTrue(validate_version("0.1.0", "0.1.0"))

        # assert that an item with a newer version 1.0.0 is valid when
        # 0.1.0 is called for
        self.assertTrue(validate_version("1.0.0", "0.1.0"))

    def test_major_version(self):
        major_version = get_major_version("1.0.1")
        self.assertEqual(major_version, "1.0.0")

        major_version = get_major_version("21.0.1")
        self.assertEqual(major_version, "21.0.0")

        with self.assertRaises(ValueError):
            get_major_version("non_numerical.0.1")
