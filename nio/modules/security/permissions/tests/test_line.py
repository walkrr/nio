from itertools import combinations
from unittest import TestCase

from nio.modules.security.permissions import PermissionsError
from nio.modules.security.permissions.line import PermissionsLine


class TestPermissionsLine(TestCase):

    def test_nominal_construction(self):
        """ Asserts all possible valid combinations of permissions
        """

        all_perms = "rwx"
        all_perm_combos = list()
        for l in range(1, len(all_perms)+1):
            all_perm_combos.extend(combinations(all_perms, l))

        for current_permset in all_perm_combos:
            # Create the PermissionsLine with the desired permissions.
            perms = PermissionsLine("".join(current_permset))

            # Ensure the permissions which are given are correct.
            self.assertEqual(perms.read, "r" in current_permset)
            self.assertEqual(perms.write, "w" in current_permset)
            self.assertEqual(perms.execute, "x" in current_permset)

            # Ensure the serialization is correct (sorted to
            # ease equality check).
            self.assertEqual(sorted(str(perms)),
                             sorted("".join(current_permset)))

    def test_bad_permission(self):
        """ Ensures that invalid permissions raise an error.
        """
        self.assertRaises(PermissionsError, PermissionsLine, "rwxa")
        self.assertRaises(PermissionsError, PermissionsLine, "arwx")
        self.assertRaises(PermissionsError, PermissionsLine, "rwxx")
        self.assertRaises(PermissionsError, PermissionsLine, "a")
        self.assertRaises(PermissionsError, PermissionsLine, "wr")
        self.assertRaises(PermissionsError, PermissionsLine, "rrw")
