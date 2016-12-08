""" Unit tests for Permissions functionality. """

from itertools import combinations
from unittest import TestCase

from nio.modules.security.permissions.permissions import (
    Permissions,
    PermissionsError,
    PermissionsLine,
    StandardPermissions
)


class TestPermissionsLine(TestCase):

    def test_nominal_construction(self):
        """ Test that all possible valid combinations of permissions
            are represented by a PermissionsLine correctly.
        """

        all_perms = "rwx"
        all_perm_combos = list()
        for l in range(1, len(all_perms)+1):
            all_perm_combos.extend(combinations(all_perms, l))

        for current_permset in all_perm_combos:
            # Create the PermissionsLine with the desired permissions.
            perms = PermissionsLine("".join(current_permset))

            # Ensure the property decorator and the attribute are
            # always in sync.
            self.assertEqual(perms._read, perms.read)
            self.assertEqual(perms._write, perms.write)
            self.assertEqual(perms._exec, perms.execute)

            # Ensure the permissions which are given are correct.
            self.assertEqual(perms.read, "r" in current_permset)
            self.assertEqual(perms.write, "w" in current_permset)
            self.assertEqual(perms.execute, "x" in current_permset)

            # Ensure the serialization is correct (sorted to
            # ease equality check).
            self.assertEqual(sorted(perms.serialized),
                             sorted("".join(current_permset)))

    def test_bad_permission(self):
        """ Ensure that specifying a non-existent permission raises
            an error.
        """
        self.assertRaises(PermissionsError, PermissionsLine, "rwxa")
        self.assertRaises(PermissionsError, PermissionsLine, "a") 


class TestStandardPermissions(TestCase):

    def test_admin_permissions(self):
        # Load the admin permissions.
        perms = Permissions(StandardPermissions.ADMIN_PERMISSIONS)

        # Check that rwx permissions are available on all blocks,
        # services, and the instance.
        self.assertTrue(perms.get("read", "services"))
        self.assertTrue(perms.get("write", "services"))
        self.assertTrue(perms.get("execute", "services"))

        self.assertTrue(perms.get("read", "blocks"))
        self.assertTrue(perms.get("write", "blocks"))
        self.assertTrue(perms.get("execute", "blocks"))

        self.assertTrue(perms.get("read", "instance"))
        self.assertTrue(perms.get("write", "instance"))
        self.assertTrue(perms.get("execute", "instance"))

        # For a made-up service and block, check rws permissions.
        self.assertTrue(perms.get("read", "services", "SkoBuffsService"))
        self.assertTrue(perms.get("write", "services", "SkoBuffsService"))
        self.assertTrue(perms.get("execute", "services", "SkoBuffsService"))

        self.assertTrue(perms.get("read", "blocks", "TheRiseIsReal"))
        self.assertTrue(perms.get("write", "blocks", "TheRiseIsReal"))
        self.assertTrue(perms.get("execute", "blocks", "TheRiseIsReal"))

    def test_read_only_permissions(self):
        # Load the read_only permissions.
        perms = Permissions(StandardPermissions.READ_ONLY_PERMISSIONS)

        # Check that r permissions are available on all blocks,
        # services, and the instance.
        self.assertTrue(perms.get("read", "services"))
        self.assertFalse(perms.get("write", "services"))
        self.assertFalse(perms.get("execute", "services"))

        self.assertTrue(perms.get("read", "blocks"))
        self.assertFalse(perms.get("write", "blocks"))
        self.assertFalse(perms.get("execute", "blocks"))

        self.assertTrue(perms.get("read", "instance"))
        self.assertFalse(perms.get("write", "instance"))
        self.assertFalse(perms.get("execute", "instance"))

        # For a made-up service and block, check r permissions.
        self.assertTrue(perms.get("read", "services", "SkoBuffsService"))
        self.assertFalse(perms.get("write", "services", "SkoBuffsService"))
        self.assertFalse(perms.get("execute", "services", "SkoBuffsService"))

        self.assertTrue(perms.get("read", "blocks", "TheRiseIsReal"))
        self.assertFalse(perms.get("write", "blocks", "TheRiseIsReal"))
        self.assertFalse(perms.get("execute", "blocks", "TheRiseIsReal"))

    def test_ops_permissions(self):
        # Load the ops permissions.
        perms = Permissions(StandardPermissions.OPS_PERMISSIONS)

        # Check that rx permissions are available on all blocks,
        # services, and the instance.
        self.assertTrue(perms.get("read", "services"))
        self.assertFalse(perms.get("write", "services"))
        self.assertTrue(perms.get("execute", "services"))

        self.assertTrue(perms.get("read", "blocks"))
        self.assertFalse(perms.get("write", "blocks"))
        self.assertTrue(perms.get("execute", "blocks"))

        self.assertTrue(perms.get("read", "instance"))
        self.assertFalse(perms.get("write", "instance"))
        self.assertTrue(perms.get("execute", "instance"))

        # For a made-up service and block, check rx permissions.
        self.assertTrue(perms.get("read", "services", "SkoBuffsService"))
        self.assertFalse(perms.get("write", "services", "SkoBuffsService"))
        self.assertTrue(perms.get("execute", "services", "SkoBuffsService"))

        self.assertTrue(perms.get("read", "blocks", "TheRiseIsReal"))
        self.assertFalse(perms.get("write", "blocks", "TheRiseIsReal"))
        self.assertTrue(perms.get("execute", "blocks", "TheRiseIsReal"))


class TestPermissions(TestCase):

    def test_shorthand_getter(self):
        json_perms = {
            "permissions": {
                "services": "rwx",
                "blocks": "rx",
                "instance": "r"
            }
        }

        # Test that an invalid JSON permissions dict is caught.
        self.assertRaises(PermissionsError,
                          Permissions,
                          json_perms["permissions"])
        perms = Permissions(json_perms)

        # Test that the service permissions all match based on the
        # input string above.
        self.assertTrue(perms.get("r", "services"))
        self.assertTrue(perms.get("w", "services"))
        self.assertTrue(perms.get("x", "services"))

        # Test that the block permissions match based on the input
        # string above.
        self.assertTrue(perms.get("r", "blocks"))
        self.assertFalse(perms.get("w", "blocks"))
        self.assertTrue(perms.get("x", "blocks"))

        # Test that the instance permissions match based on the input
        # string above.
        self.assertTrue(perms.get("r", "instance"))
        self.assertFalse(perms.get("w", "instance"))
        self.assertFalse(perms.get("x", "instance"))

    def test_longname_getter(self):
        json_perms = {
            "permissions": {
                "services": "rwx",
                "blocks": "rx",
                "instance": "r"
            }
        }

        # Test that an invalid JSON permissions dict is caught.
        self.assertRaises(PermissionsError,
                          Permissions,
                          json_perms["permissions"])
        perms = Permissions(json_perms)

        # Test that the service permissions all match based on the
        # input string above.
        self.assertTrue(perms.get("read", "services"))
        self.assertTrue(perms.get("write", "services"))
        self.assertTrue(perms.get("execute", "services"))

        # Test that the block permissions match based on the input
        # string above.
        self.assertTrue(perms.get("read", "blocks"))
        self.assertFalse(perms.get("write", "blocks"))
        self.assertTrue(perms.get("execute", "blocks"))

        # Test that the instance permissions match based on the input
        # string above.
        self.assertTrue(perms.get("read", "instance"))
        self.assertFalse(perms.get("write", "instance"))
        self.assertFalse(perms.get("execute", "instance"))

    def test_std_permissions_parsing(self):
        """ Test that the standard permission sets are parsed properly. """
        # Test the read only permission set.
        perms = Permissions(StandardPermissions.READ_ONLY_PERMISSIONS)
        self.assertTrue(perms.get("read", "instance"))
        self.assertFalse(perms.get("write", "instance"))
        self.assertFalse(perms.get("execute", "instance"))
        self.assertTrue(perms.get("read", "services"))
        self.assertFalse(perms.get("write", "services"))
        self.assertFalse(perms.get("execute", "services"))
        self.assertTrue(perms.get("read", "services", "SomeService"))
        self.assertFalse(perms.get("write", "services", "SomeService"))
        self.assertFalse(perms.get("execute", "services", "SomeService"))
        self.assertTrue(perms.get("read", "blocks"))
        self.assertFalse(perms.get("write", "blocks"))
        self.assertFalse(perms.get("execute", "blocks"))
        self.assertTrue(perms.get("read", "blocks", "SomeBlock"))
        self.assertFalse(perms.get("write", "blocks", "SomeBlock"))
        self.assertFalse(perms.get("execute", "blocks", "SomeBlock"))

        # Test the admin permission set.
        perms = Permissions(StandardPermissions.ADMIN_PERMISSIONS)
        self.assertTrue(perms.get("read", "instance"))
        self.assertTrue(perms.get("write", "instance"))
        self.assertTrue(perms.get("execute", "instance"))
        self.assertTrue(perms.get("read", "services"))
        self.assertTrue(perms.get("write", "services"))
        self.assertTrue(perms.get("execute", "services"))
        self.assertTrue(perms.get("read", "services", "SomeService"))
        self.assertTrue(perms.get("write", "services", "SomeService"))
        self.assertTrue(perms.get("execute", "services", "SomeService"))
        self.assertTrue(perms.get("read", "blocks"))
        self.assertTrue(perms.get("write", "blocks"))
        self.assertTrue(perms.get("execute", "blocks"))
        self.assertTrue(perms.get("read", "blocks", "SomeBlock"))
        self.assertTrue(perms.get("write", "blocks", "SomeBlock"))
        self.assertTrue(perms.get("execute", "blocks", "SomeBlock"))

        # Test the ops permission set.
        perms = Permissions(StandardPermissions.OPS_PERMISSIONS)
        self.assertTrue(perms.get("read", "instance"))
        self.assertFalse(perms.get("write", "instance"))
        self.assertTrue(perms.get("execute", "instance"))
        self.assertTrue(perms.get("read", "services"))
        self.assertFalse(perms.get("write", "services"))
        self.assertTrue(perms.get("execute", "services"))
        self.assertTrue(perms.get("read", "services", "SomeService"))
        self.assertFalse(perms.get("write", "services", "SomeService"))
        self.assertTrue(perms.get("execute", "services", "SomeService"))
        self.assertTrue(perms.get("read", "blocks"))
        self.assertFalse(perms.get("write", "blocks"))
        self.assertTrue(perms.get("execute", "blocks"))
        self.assertTrue(perms.get("read", "blocks", "SomeBlock"))
        self.assertFalse(perms.get("write", "blocks", "SomeBlock"))
        self.assertTrue(perms.get("execute", "blocks", "SomeBlock"))

# EOF - test_permissions.py
