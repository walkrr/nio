""" Unit tests for Permissions functionality. """

from unittest import TestCase

from nio.modules.security.permissions import (
    Permissions,
    PermissionsError
)


class TestStandardPermissions(TestCase):

    ADMIN_PERMISSIONS = {
        "services": "rwx",
        "services.*": "rwx",
        "blocks": "rwx",
        "blocks.*": "rwx",
        "instance": "rwx"
    }
    READ_ONLY_PERMISSIONS = {
        "services": "r",
        "services.*": "r",
        "blocks": "r",
        "blocks.*": "r",
        "instance": "r"
    }
    OPS_PERMISSIONS = {
        "services": "rx",
        "services.*": "rx",
        "blocks": "rx",
        "blocks.*": "rx",
        "instance": "rx"
    }

    def test_admin_permissions(self):
        """ Loads and check admin-like permissions.
        """
        perms = Permissions(TestStandardPermissions.ADMIN_PERMISSIONS)

        # Check that rwx permissions are available on all blocks,
        # services, and the instance.
        self.assertTrue(perms.get("services", "read"))
        self.assertTrue(perms.get("services", "write"))
        self.assertTrue(perms.get("services", "execute"))

        self.assertTrue(perms.get("blocks", "read"))
        self.assertTrue(perms.get("blocks", "write"))
        self.assertTrue(perms.get("blocks", "execute"))

        self.assertTrue(perms.get("instance", "read"))
        self.assertTrue(perms.get("instance", "write"))
        self.assertTrue(perms.get("instance", "execute"))

        # For a made-up service and block, check rws permissions.
        self.assertTrue(perms.get("services.SkoBuffsService", "read"))
        self.assertTrue(perms.get("services.SkoBuffsService", "write"))
        self.assertTrue(perms.get("services.SkoBuffsService", "execute"))

        self.assertTrue(perms.get("blocks.TheRiseIsReal", "read"))
        self.assertTrue(perms.get("blocks.TheRiseIsReal", "write"))
        self.assertTrue(perms.get("blocks.TheRiseIsReal", "execute"))

    def test_read_only_permissions(self):
        """ Loads and check read_only-like permissions.
        """
        perms = Permissions(TestStandardPermissions.READ_ONLY_PERMISSIONS)

        # Check that r permissions are available on all blocks,
        # services, and the instance.
        self.assertTrue(perms.get("services", "read"))
        self.assertFalse(perms.get("services", "write"))
        self.assertFalse(perms.get("services", "execute"))

        self.assertTrue(perms.get("blocks", "read"))
        self.assertFalse(perms.get("blocks", "write"))
        self.assertFalse(perms.get("blocks", "execute"))

        self.assertTrue(perms.get("instance", "read"))
        self.assertFalse(perms.get("instance", "write"))
        self.assertFalse(perms.get("instance", "execute"))

        # For a made-up service and block, check r permissions.
        self.assertTrue(perms.get("services.SkoBuffsService", "read"))
        self.assertFalse(perms.get("services.SkoBuffsService", "write"))
        self.assertFalse(perms.get("services.SkoBuffsService", "execute"))

        self.assertTrue(perms.get("blocks.TheRiseIsReal", "read"))
        self.assertFalse(perms.get("blocks.TheRiseIsReal", "write"))
        self.assertFalse(perms.get("blocks.TheRiseIsReal", "execute"))

    def test_ops_permissions(self):
        """ Loads and check read and execute permissions.
        """
        perms = Permissions(TestStandardPermissions.OPS_PERMISSIONS)

        # Check that rx permissions are available on all blocks,
        # services, and the instance.
        self.assertTrue(perms.get("services", "read"))
        self.assertFalse(perms.get("services", "write"))
        self.assertTrue(perms.get("services", "execute"))

        self.assertTrue(perms.get("blocks", "read"))
        self.assertFalse(perms.get("blocks", "write"))
        self.assertTrue(perms.get("blocks", "execute"))

        self.assertTrue(perms.get("instance", "read"))
        self.assertFalse(perms.get("instance", "write"))
        self.assertTrue(perms.get("instance", "execute"))

        # For a made-up service and block, check rx permissions.
        self.assertTrue(perms.get("services.SkoBuffsService", "read"))
        self.assertFalse(perms.get("services.SkoBuffsService", "write"))
        self.assertTrue(perms.get("services.SkoBuffsService", "execute"))

        self.assertTrue(perms.get("blocks.TheRiseIsReal", "read"))
        self.assertFalse(perms.get("blocks.TheRiseIsReal", "write"))
        self.assertTrue(perms.get("blocks.TheRiseIsReal", "execute"))


class TestPermissions(TestCase):

    def test_shorthand_getter(self):
        """ Asserts that permissions can be obtained using 'shorthand' notations
        """
        json_perms = {
            "services": "rwx",
            "blocks": "rx",
            "instance": "r"
        }

        perms = Permissions(json_perms)

        # Test that the service permissions all match based on the
        # input string above.
        self.assertTrue(perms.get("services", "r"))
        self.assertTrue(perms.get("services", "w"))
        self.assertTrue(perms.get("services", "x"))

        # Test that the block permissions match based on the input
        # string above.
        self.assertTrue(perms.get("blocks", "r"))
        self.assertFalse(perms.get("blocks", "w"))
        self.assertTrue(perms.get("blocks", "x"))

        # Test that the instance permissions match based on the input
        # string above.
        self.assertTrue(perms.get("instance", "r"))
        self.assertFalse(perms.get("instance", "w"))
        self.assertFalse(perms.get("instance", "x"))

    def test_longname_getter(self):
        """ Asserts that permissions can be obtained using explicit notations
        """
        json_perms = {
            "services": "rwx",
            "blocks": "rx",
            "instance": "r"
        }

        # Test that an invalid JSON permissions dict is caught.
        self.assertRaises(PermissionsError,
                          Permissions,
                          ["services"])
        perms = Permissions(json_perms)

        # Test that the service permissions all match based on the
        # input string above.
        self.assertTrue(perms.get("services", "read"))
        self.assertTrue(perms.get("services", "write"))
        self.assertTrue(perms.get("services", "execute"))

        # Test that the block permissions match based on the input
        # string above.
        self.assertTrue(perms.get("blocks", "read"))
        self.assertFalse(perms.get("blocks", "write"))
        self.assertTrue(perms.get("blocks", "execute"))

        # Test that the instance permissions match based on the input
        # string above.
        self.assertTrue(perms.get("instance", "read"))
        self.assertFalse(perms.get("instance", "write"))
        self.assertFalse(perms.get("instance", "execute"))

    def test_std_permissions_parsing(self):
        """ Test that the standard permission sets are parsed properly.
        """

        # Test the read only permission set.
        perms = Permissions(TestStandardPermissions.READ_ONLY_PERMISSIONS)
        self.assertTrue(perms.get("instance", "read"))
        self.assertFalse(perms.get("instance", "write"))
        self.assertFalse(perms.get("instance", "execute"))
        self.assertTrue(perms.get("services", "read"))
        self.assertFalse(perms.get("services", "write"))
        self.assertFalse(perms.get("execute", "services"))
        self.assertTrue(perms.get("services.SomeService", "read"))
        self.assertFalse(perms.get("services.SomeService", "write"))
        self.assertFalse(perms.get("services.SomeService", "execute"))
        self.assertTrue(perms.get("blocks", "read"))
        self.assertFalse(perms.get("blocks", "write"))
        self.assertFalse(perms.get("blocks", "execute"))
        self.assertTrue(perms.get("blocks.SomeBlock", "read"))
        self.assertFalse(perms.get("blocks.SomeBlock", "write"))
        self.assertFalse(perms.get("blocks.SomeBlock", "execute"))

        # Test the admin permission set.
        perms = Permissions(TestStandardPermissions.ADMIN_PERMISSIONS)
        self.assertTrue(perms.get("instance", "read"))
        self.assertTrue(perms.get("instance", "write"))
        self.assertTrue(perms.get("instance", "execute"))
        self.assertTrue(perms.get("services", "read"))
        self.assertTrue(perms.get("services", "write"))
        self.assertTrue(perms.get("services", "execute"))
        self.assertTrue(perms.get("services.SomeService", "read"))
        self.assertTrue(perms.get("services.SomeService", "write"))
        self.assertTrue(perms.get("services.SomeService", "execute"))
        self.assertTrue(perms.get("blocks", "read"))
        self.assertTrue(perms.get("blocks", "write"))
        self.assertTrue(perms.get("blocks", "execute"))
        self.assertTrue(perms.get("blocks.SomeBlock", "read"))
        self.assertTrue(perms.get("blocks.SomeBlock", "write"))
        self.assertTrue(perms.get("blocks.SomeBlock", "execute"))

        # Test the ops permission set.
        perms = Permissions(TestStandardPermissions.OPS_PERMISSIONS)
        self.assertTrue(perms.get("instance", "read"))
        self.assertFalse(perms.get("instance", "write"))
        self.assertTrue(perms.get("instance", "execute"))
        self.assertTrue(perms.get("services", "read"))
        self.assertFalse(perms.get("services", "write"))
        self.assertTrue(perms.get("services", "execute"))
        self.assertTrue(perms.get("services.SomeService", "read"))
        self.assertFalse(perms.get("services.SomeService", "write"))
        self.assertTrue(perms.get("services.SomeService", "execute"))
        self.assertTrue(perms.get("blocks", "read"))
        self.assertFalse(perms.get("blocks", "write"))
        self.assertTrue(perms.get("blocks", "execute"))
        self.assertTrue(perms.get("blocks.SomeBlock", "read"))
        self.assertFalse(perms.get("blocks.SomeBlock", "write"))
        self.assertTrue(perms.get("blocks.SomeBlock", "execute"))

    def test_permissions(self):
        """ Asserts a variety of permissions
        """
        perms = Permissions({
           "services": "r",
           "services.*": "r",
           "services.MyService1": "x",
           "blocks": "rw",
           "blocks.*": "r",
           "blocks.MyBlock1": "wx",
           "instance": "rw"
        })

        # due to "services": "r"
        self.assertTrue(perms.get("services", "read"))
        self.assertFalse(perms.get("services", "write"))
        self.assertFalse(perms.get("services", "execute"))
        # true due to "services.*": "r"
        self.assertTrue(perms.get("services.MyService1", "read"))
        self.assertFalse(perms.get("services.MyService1", "write"))
        # true due to "services.MyService1": "x"
        self.assertTrue(perms.get("services.MyService1", "execute"))
        # true due to "services.*": "r"
        self.assertTrue(perms.get("services.MyService2", "read"))
        self.assertFalse(perms.get("services.MyService2", "write"))
        self.assertFalse(perms.get("services.MyService2", "execute"))

        # true due to "blocks": "rw"
        self.assertTrue(perms.get("blocks", "read"))
        # true due to "blocks": "rw"
        self.assertTrue(perms.get("blocks", "write"))
        self.assertFalse(perms.get("blocks", "execute"))
        # true due to "blocks.*": "r"
        self.assertTrue(perms.get("blocks.MyBlock1", "read"))
        # true due to "blocks.MyBlock1": "wx"
        self.assertTrue(perms.get("blocks.MyBlock1", "write"))
        self.assertTrue(perms.get("blocks.MyBlock1", "execute"))
        # true due to "blocks.*": "r"
        self.assertTrue(perms.get("blocks.MyBlock2", "read"))
        self.assertFalse(perms.get("blocks.MyBlock2", "write"))
        self.assertFalse(perms.get("blocks.MyBlock2", "execute"))

        # true due to "instance": "rw"
        self.assertTrue(perms.get("instance", "read"))
        self.assertTrue(perms.get("instance", "write"))
        self.assertFalse(perms.get("instance", "execute"))

    def test_permission_setter(self):
        """ Asserts permissions setting functionality
        """
        perms = Permissions()
        perms.set("services", "read")
        perms.set("services.*", "read")
        perms.set("services.MyService1", "execute")

        perms.set("blocks", "read")
        perms.set("blocks", "write")
        perms.set("blocks.*", "read")
        perms.set("blocks.MyBlock1", "write")
        perms.set("blocks.MyBlock1", "execute")

        perms.set("instance", "read")
        perms.set("instance", "write")

        # Test that the service permissions all match based on the
        # setter.
        self.assertTrue(perms.get("services", "read"))
        self.assertFalse(perms.get("services", "write"))
        self.assertFalse(perms.get("services", "execute"))
        self.assertTrue(perms.get("services.MyService1", "read"))
        self.assertFalse(perms.get("services.MyService1", "write"))
        self.assertTrue(perms.get("services.MyService1", "execute"))
        self.assertTrue(perms.get("services.MyService2", "read"))
        self.assertFalse(perms.get("services.MyService2", "write"))
        self.assertFalse(perms.get("services.MyService2", "execute"))

        # Test that the block permissions match based on the input
        # setter.
        self.assertTrue(perms.get("blocks", "read"))
        self.assertTrue(perms.get("blocks", "write"))
        self.assertFalse(perms.get("blocks", "execute"))
        self.assertTrue(perms.get("blocks.MyBlock1", "read"))
        self.assertTrue(perms.get("blocks.MyBlock1", "write"))
        self.assertTrue(perms.get("blocks.MyBlock1", "execute"))
        self.assertTrue(perms.get("blocks.MyBlock2", "read"))
        self.assertFalse(perms.get("blocks.MyBlock2", "write"))
        self.assertFalse(perms.get("blocks.MyBlock2", "execute"))

        # Test that the instance permissions match based on the input
        # setter.
        self.assertTrue(perms.get("instance", "read"))
        self.assertTrue(perms.get("instance", "write"))
        self.assertFalse(perms.get("instance", "execute"))

