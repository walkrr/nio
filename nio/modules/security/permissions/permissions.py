from re import match
from re import compile as re_compile
from sre_constants import error as RegexError

from nio.modules.security.permissions import PermissionsError
from nio.modules.security.permissions.line import PermissionsLine


class Permissions(object):
    """
    Class which can be loaded a JSON block indicating permissions, or set
    on the fly.

    ---- Loading ----
    The incoming JSON block should be formatted as:
    {
        <resource1>: <permissions_string>,
        <resource2>: <permissions_string>,
        <resourceN>: <permissions_string>
    }

    Note that each resource needs to be a valid regular expression, so that
    later when getting a given resource permission through a 'get' operation,
    the incoming resource can be 'matched' against the above definitions using
    regular expression matching.

    The permissions schema works on a white-list theory, no entries for
    specific resources would equate to no access for a user.

    Specific permissions to a resource can be specified by name,
    keeping in mind that a wildcard permission will be "in addition
    to" rather than "overridden by" a specific permission.
    For example:
        "services.MyService1": <permissions_string>,
        "blocks.*": <permissions_string>

    ---- Storing / Loading ----
    Once permissions are loaded, they are stored in this class under the
    <_permissions> member dict with the following structure:
    {
        <resource1>: PermissionsLine(<resource1_value_from_load>),
        <resource2>: PermissionsLine(<resource2_value_from_load>),
        <resourceN>: PermissionsLine(<resourceN_value_from_load>),
    }

    ---- Queries ----
    Querying a permission is done via the get() member function.

    ---- Setting a permission ----
    Setting a permission can additionally be done via the set() method

    """

    def __init__(self, permissions=None):
        """ Initializes a permission instance

        Args:
            permissions (dict): Initial permissions to load
        """

        # Default to no permissions.
        self._permissions = {}

        # Load permissions if specified
        if permissions:
            self.load(permissions)

    def load(self, permissions):
        """ Loads a dictionary of permissions

        Args:
            permissions (dict): permission specifications

        Raises:
            PermissionError if an invalid permission spec. is found
        """
        # Check that the permissions block has the proper structure.
        if not isinstance(permissions, dict):
            raise PermissionsError("No valid 'permissions' specified.")

        # For each key in the incoming block, parse the permissions out into
        # the proper structure.
        for regex, perm_str in permissions.items():

            try:
                # validate regex at this level
                re_compile(regex)
                self._permissions[regex] = PermissionsLine(perm_str)
            except RegexError:
                raise PermissionsError("'{0}' is not a valid regex for "
                                       " matching permissions.".format(regex))

    def get(self, resource, permission):
        """ Finds out if resource has given permission

        Args:
            resource: Specific service to request permission for.
            permission: The permission to check.

        Returns:
            True if permission is present, otherwise False.
        """

        # Ensure the permission being requested is valid, mapping to the
        # shorthand permission if necessary.
        permission = permission.lower()
        if permission in PermissionsLine.SHORTHAND:
            permission = PermissionsLine.SHORTHAND[permission]

        for pattern, permissions in self._permissions.items():
            # add a $ to match the end of the string (otherwise it would match
            # sub-strings, i.e., "blocks" would match "blocks.MyBlock")
            m = match("{}$".format(pattern), resource)
            if m and getattr(permissions, permission, False):
                return True
        return False

    def set(self, resource, permission, value=True):
        """ Sets a permission on given resource

        In addition to loading permissions from a dictionary during
        creation, permissions can be set explicitly

        Args:
            resource (str): Specific resource being assigned a permission.
            permission (str): The permission to check.
            value (bool): Permission value to use

        Raises:
            PermissionError if an invalid permission spec. is specified
        """

        # Make sure the value for the permission is valid (True or False only).
        if value not in [True, False]:
            raise PermissionsError("Unable to assign permission value '{0}'. "
                                   "Must be True or False.".format(value))

        # Ensure the permission being requested is valid, mapping to the
        # shorthand permission if necessary.
        permission = permission.lower()
        if permission in PermissionsLine.SHORTHAND:
            permission = PermissionsLine.SHORTHAND[permission]

        try:
            # make sure resource is a valid regex
            re_compile(resource)
        except RegexError:
            raise PermissionsError("'{0}' is not a valid regex for "
                                   " matching permissions.".format(resource))

        if resource not in self._permissions:
            self._permissions[resource] = PermissionsLine()

        # assign actual permission
        setattr(self._permissions[resource], permission, value)

    def to_dict(self):
        """ Return a serializable dictionary of the permissions

        Returns:
            dict: keys are resource permission regexes, values are shorthand
            strings representing the permissions on that resource
        """
        return {
            resource_regex: str(line)
            for resource_regex, line in self._permissions.items()
        }

    def update(self, perms):
        """ Update the current Permissions object with another permissions
            object, with the second (argument) taking priority over the
            original if there is a key collision.

            Returns:
               Permissions object.
        """

        self.load(perms.to_dict())
        return self
