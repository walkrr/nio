"""
permissions : {
    # Service level permissions:
    #  r: Can view a service.
    #  w: Can edit a service (routing/blocks/etc...).
    #  x: Can start/stop a service.
    "services" : "rwx",

    # Block level permissions:
    #  r: Can view a block and it's configuration.
    #  w: Can modify a block's configuration.
    #  x: Can command a block.
    "blocks": "rwx",

    # Instance level permissions:
    #  r: Can view an instance.
    #  w: Can edit an instance (access to instance, etc...)
    #  x: Can delete an instance.
    "instance": "rwx"
}
"""

from re import match
from re import compile as re_compile
from sre_constants import error as RegexError

class PermissionsError(Exception):
    pass

class PermissionsLine(object):

    TARGETS = ["read", "write", "execute"]
    SHORTHAND = {"r": "read", "w": "write", "x": "execute"}

    def __init__(self, entry=""):
        self._raw_perms = self._parse_entry(entry.lower())
        self._read = "r" in self._raw_perms
        self._write = "w" in self._raw_perms
        self._exec = "x" in self._raw_perms
        
    def _parse_entry(self, entry):
        r = str()
        opts = set(PermissionsLine.SHORTHAND.keys())
        for c in entry:
           if c not in opts:
               raise PermissionsError("Invalid permssion setting '{0}'".format(c))
           r += c
        return r

    @property
    def read(self):
        return self._read

    @read.setter
    def read(self, value):
        self._read = value

    @property
    def write(self):
        return self._write

    @write.setter
    def write(self, value):
        self._write = value

    @property
    def execute(self):
        return self._exec

    @execute.setter
    def execute(self, value):
        self._exec = value

    @property
    def serialized(self):
        r = "r" if self.read else ""
        r += "w" if self.write else ""
        r += "x" if self.execute else ""
        return r

class Permissions(object):
    """
    Class which can be loaded a JSON block indicating permissions, or set
    on the fly and serialized.

    ---- Loading ----
    The incoming JSON block should be formatted as:
    {"permissions": {
        # Base resource permissions, all of which are required.
        "services": <permissions_string>,
        "blocks": <permissions_string>,
        "instance": <permissions_string>,

        # Specific resource permissions, none of which are required by
        # the permissions module, but since the permissions schema works
        # on a whitelist theory, no entries for specific resources would
        # equate to no access for a user.

        # While * is not a valid regex in itself, we treat it as "any"
        # for user ease of use.
        "services.*": <permissions_string>,
        "blocks.*": <permissions_string>,

        # Specific permissions to a resource can be specified by name,
        # keeping in mind that a wildcard permission will be "in addition
        # to" rather than "overridden by" a specific permission.
        "services.MyService1": <permissions_string>,
        "blocks.MyBlock1": <permissions_string>
    }

    ---- Storing ----
    Once a permission is loaded, it is stored in this class under the
    <_perm_map> member dict with the following structure:
    {
        # The top level service and block permissions are pulled directly
        # from the input JSON block and wrapped up in a PermissionsLine.
        "services": PermissionsLine(<services_value_from_load>),
        "blocks": PermissionsLine(<blocks_value_from_load>),
        "instance": PermissionsLine(<instance_value_from_load>),

        # Any specific permissions live under a different key, so that lookups
        # can be done without iterating through a potentially massive dictionary.
        "_services": {
            ".*": PermissionsLine(...),
            "MyService1": PermissionsLine(...)
        }
        "_blocks": {
            ".*": PermissionsLine(...),
            "MyBlock1": PermissionsLine(...)
        }
    }

    ---- Queries ----
    Querying a permission is done via the get() member function.
    >>> permissions.get("read", "blocks")
    Value of _perm_map["blocks"].read
    >>> permissions.get("read", "blocks", "MyBlock1")
    Value of (_perm_map["_blocks"]["MyBlock1"].read ||
              _perm_map["_blocks"][<regex_matching_"MyBlock1">].read)
    """

    TARGETS = ["services", "blocks", "instance"]
    SUBTARGETS = ["_services", "_blocks"]

    def __init__(self, perms_block=None):
        # Default permissions to nothing.
        self._perm_map = {t: PermissionsLine() for t in Permissions.TARGETS}
        for sub in Permissions.SUBTARGETS:
            self._perm_map[sub] = dict()
        if perms_block:
            self.load(perms_block)

    def load(self, perms_block):
        # Check that the permissions block has the proper structure.
        if not "permissions" in perms_block or\
           not isinstance(perms_block["permissions"], dict):
            raise PermissionsError("No valid 'permissions' block specified.")

        # For each key in the incoming block, parse the permissions out into
        # the proper structure.
        for key, perm_str in perms_block["permissions"].items():
            key = key.lower()
            if key in Permissions.TARGETS:
                self._perm_map[key] = PermissionsLine(perm_str)
                continue

            # If a subtarget is specified, parse out the value and target.
            if key.count(".") != 1:
                raise PermissionsError("Invalid permissions specifier '{0}'"\
                                       .format(key))

            # Build the subtarget key and convert the wildcard to an actual
            # regex.
            key, subtarget = key.split(".")
            subtarget = ".*" if subtarget == "*" else subtarget
            subkey = "_" + key
            if subkey not in Permissions.SUBTARGETS:
                raise PermissionsError("Invalid permissions specifier '{0}'"\
                                       .format(key))               
            try:
                re_compile(subtarget)
                self._perm_map[subkey][subtarget] = PermissionsLine(perm_str)
            except RegexError:
                raise PermissionsError("'{0}' is not a valid regex for "\
                                       " matching permissions.".format(subtarget))

    def get(self, perm, target, subtarget=None):
        """
        Return True if a service (specified by <target>) has the <perm>
        permission, otherwise return False.

        Args:
            - target: Specific service to request permission for, None for
                      the generic "services" permissions.
            - perm: The permission to check.

        Returns:
            True if permission is present, otherwise False.
        """

        # Ensure the permission being requested is valid, mapping to the
        # shorthand permission if necessary.
        perm = perm.lower()
        if perm in PermissionsLine.SHORTHAND:
            perm = PermissionsLine.SHORTHAND[perm]
        elif perm not in PermissionsLine.TARGETS:
            raise PermissionsError("'{0}' is not a valid permissions specifier."\
                                   .format(perm))

        if subtarget:
            target = "_" + target
            if not self._perm_map.get(target):
                raise PermissionsError("Unable to query {0}. Invalid permission"\
                                       " specifier.".format(target))
            for regx, perms in self._perm_map[target].items():
                m = match(regx, subtarget)
                if m and m.group() and getattr(perms, perm, False):
                    return True
            return False

        return getattr(self._perm_map[target], perm, False)


class StandardPermissions(object):
    """ Collection class for standard permission sets. """

    # Give a user Read only access to everything in the instance.
    READ_ONLY_PERMISSIONS = {
        "permissions": {
            "services": "r",
            "services.*" : "r",
            "blocks": "r",
            "blocks.*": "r",
            "instance": "r"
        }
    }
    # Give a user full permissions across the instance.
    ADMIN_PERMISSIONS = {
        "permissions": {
            "services": "rwx",
            "services.*": "rwx",
            "blocks": "rwx",
            "blocks.*": "rwx",
            "instance": "rwx"
        }
    }

    # Give a user ability to execute and view a permission.
    OPS_PERMISSIONS = {
        "permissions": {
            "services": "rx",
            "services.*": "rx",
            "blocks": "rx",
            "blocks.*": "rx",
            "instance": "rx"
        }
    }

# EOF - permissions.py
