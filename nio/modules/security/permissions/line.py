class PermissionsError(Exception):
    pass


class PermissionsLine(object):

    """ Defines allowed permissions

    {
        # Resource level permissions:
        #  r: Can view a resource.
        #  w: Can edit a resource
        #  x: Can perform an execute operation like start/stop a resource.
    }

    Permissions can be specified as a combination of the above while keeping
    the order (see ALLOWED_PERMISSIONS).

    """

    ALLOWED_PERMISSIONS = ['r', 'w', 'x', 'rw', 'rx', 'wx', 'rwx']
    TARGETS = ["read", "write", "execute"]
    SHORTHAND = {"r": "read", "w": "write", "x": "execute"}

    def __init__(self, permissions=""):
        """ Initialized a permission line

        Args:
            permissions (string): Permissions to initialize line with
        """

        # allow uppercase definitions
        raw_perms = permissions.lower()
        if raw_perms and raw_perms not in PermissionsLine.ALLOWED_PERMISSIONS:
            raise PermissionsError("Invalid permission setting '{0}'".
                                   format(raw_perms))
        # assign permissions
        self.read = "r" in raw_perms
        self.write = "w" in raw_perms
        self.execute = "x" in raw_perms

    def __str__(self):
        r = "r" if self.read else ""
        r += "w" if self.write else ""
        r += "x" if self.execute else ""
        return r
